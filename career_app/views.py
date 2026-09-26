import traceback
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

from .models import Opportunity, ProfileMatch, StudentProfile, AcademicRecord, ResumeAnalysis
from .serializers import OpportunitySerializer, ProfileMatchSerializer, StudentProfileSerializer, AcademicRecordSerializer, ResumeAnalysisSerializer
from .ml_pipeline import analyze_resume
from .tasks import run_universal_scraper
import os
import logging
from rest_framework import viewsets

logger = logging.getLogger(__name__)

class StudentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return StudentProfile.objects.none()
        return StudentProfile.objects.filter(user=self.request.user)

class AcademicRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return AcademicRecord.objects.none()
        return AcademicRecord.objects.filter(student__user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class UploadResumeAPIView(APIView):
    """Parses resume PDF, stores profile in DB, and queues match scoring."""
    def post(self, request, *args, **kwargs):
        resume_file = request.FILES.get('resume')
        if not resume_file:
            return Response({"error": "No PDF file supplied."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. AI Parsing Pipeline
            analysis = analyze_resume(resume_file.read())

            # 2. Persist to MySQL
            user_id = request.data.get('user_id')
            user_obj = request.user if request.user.is_authenticated else None
            
            if not user_obj and user_id:
                try:
                    user_obj = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    pass

            if user_obj:
                profile, _ = StudentProfile.objects.get_or_create(user=user_obj)
                profile.full_name = analysis.full_name
            else:
                profile = StudentProfile.objects.create(full_name=analysis.full_name)

            profile.target_role = analysis.target_professions[0] if analysis.target_professions else "Junior Analyst"
            profile.current_skills = analysis.extracted_skills
            profile.skill_gaps = analysis.skill_gaps
            profile.resume_improvements = analysis.resume_improvements
            profile.interview_questions = analysis.interview_questions
            profile.bio = analysis.summary
            profile.projects = analysis.projects
            profile.experience = analysis.experience
            
            # Dynamic Readiness Calculation
            penalty = len(analysis.skill_gaps) * 8
            profile.readiness_score = max(35, 100 - penalty)
            profile.save()

            # Record History
            if user_obj:
                ResumeAnalysis.objects.create(
                    user=user_obj,
                    resume_file=resume_file,
                    target_role=profile.target_role,
                    current_skills=profile.current_skills,
                    skill_gaps=profile.skill_gaps,
                    resume_improvements=profile.resume_improvements,
                    interview_questions=profile.interview_questions,
                    projects=profile.projects,
                    experience=profile.experience,
                    readiness_score=profile.readiness_score
                )

            # Save academic records (profile must be saved first so FK exists)
            profile.academics.all().delete()
            for record in analysis.academic_records:
                try:
                    AcademicRecord.objects.create(
                        student=profile,
                        degree=str(record.get('degree', 'Unknown Degree'))[:150],
                        institution=str(record.get('institution', 'Unknown Institution'))[:200],
                        graduation_year=int(record.get('graduation_year', 2024)),
                        cgpa=float(record.get('cgpa', 0.0))
                    )
                except Exception as e:
                    logger.warning(f"Failed to save academic record {record}: {e}")

            # 3. Trigger Celery Asynchronous Scraper (which chains match scoring)
            try:
                run_universal_scraper.delay(profile.id)
            except Exception as e:
                logger.warning(f"Background tasks skipped (Redis may be down): {e}")

            return Response({
                "profile_id": profile.id,
                "full_name": profile.full_name,
                "target_role": profile.target_role,
                "readiness_score": profile.readiness_score,
                "extracted_skills": profile.current_skills,
                "skill_gaps": profile.skill_gaps,
                "recommended_courses": analysis.recommended_courses,
                "resume_improvements": profile.resume_improvements,
                "interview_questions": profile.interview_questions,
                "bio": profile.bio,
                "projects": profile.projects,
                "experience": profile.experience,
                "academic_records": [
                    {"degree": r.degree, "institution": r.institution, "graduation_year": r.graduation_year, "cgpa": float(r.cgpa)}
                    for r in profile.academics.all()
                ]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            error_msg = str(e)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            # Map known errors to appropriate HTTP responses
            if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
                error_msg = "AI provider rate limit exceeded. Please wait about 30 seconds and try again."
            elif "404" in error_msg or "NOT_FOUND" in error_msg:
                status_code = status.HTTP_502_BAD_GATEWAY
                error_msg = "AI provider model not found or currently unavailable."
            elif "API_KEY" in error_msg or "api_key" in error_msg:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                error_msg = "Server configuration error: Google API Key is missing or invalid."
            elif "PDF" in error_msg.upper() or "decode" in error_msg.lower() or "EOF" in error_msg:
                status_code = status.HTTP_400_BAD_REQUEST
                error_msg = "Failed to parse the uploaded PDF. Please ensure it is a valid, readable text PDF."
                
            return Response({"error": error_msg, "details": str(e)}, status=status_code)

class ResumeAnalysisHistoryAPIView(generics.ListAPIView):
    """Fetch all past resume analysis results for the logged-in user."""
    serializer_class = ResumeAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ResumeAnalysis.objects.filter(user=self.request.user).order_by('-created_at')


class OpportunityListAPIView(generics.ListAPIView):
    """Search and filter catalog of opportunities."""
    queryset = Opportunity.objects.filter(is_active=True)
    serializer_class = OpportunitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'provider', 'description', 'required_skills__skill_name']
    ordering_fields = ['created_at', 'title', 'deadline']
    ordering = ['-created_at']

    def get_queryset(self):
        search_query = self.request.query_params.get('search')
        if search_query:
            """
            from .adapters.universal_scraper import UniversalScraperAdapter
            from .models import OpportunitySkill
            from django.db import transaction
            try:
                adapter = UniversalScraperAdapter()
                raw_records = adapter.fetch_all(search_query)
                for norm in raw_records:
                    skills = norm.pop("skills", [])
                    with transaction.atomic():
                        opp, created = Opportunity.objects.update_or_create(
                            dedupe_hash=norm["dedupe_hash"],
                            defaults=norm
                        )
                        for s in skills:
                            OpportunitySkill.objects.get_or_create(
                                opportunity=opp,
                                skill_name=s.strip()
                            )
            except Exception as e:
                print(f"Dynamic scraping error: {e}")
            """
            # Note: We rely on the Celery background worker to populate opportunities. 
            # Inline blocking scraping is removed to prevent 'database is locked' errors on SQLite.
            pass

        qs = Opportunity.objects.filter(is_active=True)
        opp_type = self.request.query_params.get('type')
        is_free = self.request.query_params.get('is_free')

        if opp_type:
            qs = qs.filter(opportunity_type__icontains=opp_type)
        if is_free is not None and is_free != '':
            qs = qs.filter(is_free=(is_free.lower() == 'true'))
        return qs.distinct()

class OpportunityTypesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        types = Opportunity.objects.exclude(opportunity_type='').values_list('opportunity_type', flat=True).distinct()
        return Response([t for t in types])


class RecommendedMatchesAPIView(APIView):
    """Retrieves ranked opportunities for the authenticated user's profile."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        matches = ProfileMatch.objects.filter(profile=profile).select_related('opportunity')
        
        # Categorize matches for the frontend
        schemes = [m for m in matches if m.opportunity.opportunity_type == 'Scheme']
        others = [m for m in matches if m.opportunity.opportunity_type != 'Scheme']

        return Response({
            "schemes": ProfileMatchSerializer(schemes, many=True).data,
            "opportunities": ProfileMatchSerializer(others, many=True).data
        })

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

@method_decorator(csrf_exempt, name='dispatch')
class SocialLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo['email']
            name = idinfo.get('name', 'Student')
            
            user, created = User.objects.get_or_create(username=email, defaults={'email': email, 'first_name': name})
            login(request, user)
            return Response({"message": "Successfully logged in", "user_id": user.id})
        except ValueError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        context_msg = "You are a helpful CareerAI chatbot."
        profile_id = None
        try:
            profile = StudentProfile.objects.get(user=request.user)
            profile_id = profile.id
            context_msg += f"\nThe user is a {profile.target_role} with skills: {', '.join(profile.current_skills)}."
        except StudentProfile.DoesNotExist:
            pass
                
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", google_api_key=api_key, temperature=0.7)
            try:
                response = llm.invoke(f"{context_msg}\n\nUser: {message}\nAI:")
                return Response({"response": response.content})
            except Exception as e:
                # API failed (likely 429 quota exhausted). Fallback to local heuristic.
                pass
                
        # --- LOCAL NLP FALLBACK ---
        local_context = "I am CareerAI, your local career assistant! "
        if profile_id:
            try:
                profile = StudentProfile.objects.get(id=profile_id)
                local_context += f"I see you're interested in being a {profile.target_role}. "
            except StudentProfile.DoesNotExist:
                pass
                
        msg_lower = message.lower()
        if any(word in msg_lower for word in ["hello", "hi", "hey"]):
            ai_text = f"{local_context}How can I help you with your career goals today?"
        elif any(word in msg_lower for word in ["resume", "cv"]):
            ai_text = "I recommend highlighting your technical skills at the top of your resume and quantifying your achievements with metrics."
        elif any(word in msg_lower for word in ["interview", "prep"]):
            ai_text = "For interviews, always use the STAR method (Situation, Task, Action, Result) to structure your behavioral answers."
        elif any(word in msg_lower for word in ["course", "learn", "study"]):
            ai_text = "I recommend checking out SWAYAM or NPTEL for certified courses. I can match you with specific courses if you upload your resume."
        elif any(word in msg_lower for word in ["job", "internship", "scheme"]):
            ai_text = "You can browse the Opportunity Hub tab to see the latest jobs, internships, and government schemes matching your profile."
        else:
            ai_text = "That's an interesting point! I am currently running on my lightweight offline model due to high demand, but I recommend uploading your resume to get the most tailored career advice."

        return Response({"response": ai_text})

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Successfully logged in", "user_id": user.id, "username": user.username}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")
        
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, email=email, password=password)
        StudentProfile.objects.create(user=user, target_role='Student')
        
        login(request, user)
        return Response({"message": "Registration successful", "user_id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)

class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

# get_object_or_404 is imported at the top of the file

class ToggleBookmarkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, opp_id, *args, **kwargs):
        opportunity = get_object_or_404(Opportunity, id=opp_id)
        profile = get_object_or_404(StudentProfile, user=request.user)
        match, created = ProfileMatch.objects.get_or_create(
            profile=profile,
            opportunity=opportunity,
            defaults={'relevance_score': 50.0, 'reasoning': "Manually interacted by user."}
        )
        match.is_bookmarked = not match.is_bookmarked
        match.save()
        return Response({"is_bookmarked": match.is_bookmarked}, status=status.HTTP_200_OK)

class GenerateCoverLetterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, opp_id, *args, **kwargs):
        opportunity = get_object_or_404(Opportunity, id=opp_id)
        profile = get_object_or_404(StudentProfile, user=request.user)
        
        # Check if we already have a generated cover letter for this match
        match, created = ProfileMatch.objects.get_or_create(
            profile=profile,
            opportunity=opportunity,
            defaults={'relevance_score': 50.0, 'reasoning': "Interacted via cover letter generation."}
        )
        
        if match.cover_letter:
            return Response({"cover_letter": match.cover_letter}, status=status.HTTP_200_OK)
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return Response({"error": "LLM API Key missing"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", google_api_key=api_key, temperature=0.7)
        prompt = f"""
        Write a professional cover letter for the following job opportunity.
        Candidate Name: {profile.full_name}
        Target Role: {profile.target_role}
        Candidate Skills: {', '.join(profile.current_skills)}
        
        Job Title: {opportunity.title}
        Company/Provider: {opportunity.provider}
        Job Description: {opportunity.description}
        
        The cover letter should be concise, professional, and highlight the alignment between the candidate's skills and the job requirements.
        """
        try:
            response = llm.invoke(prompt)
            cover_letter = response.content
            if isinstance(cover_letter, list):
                cover_letter = "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in cover_letter])
            
            # Save the generated cover letter to the database
            match.cover_letter = cover_letter
            match.save(update_fields=['cover_letter'])
            
            return Response({"cover_letter": cover_letter}, status=status.HTTP_200_OK)
        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "unavailable" in error_str:
                return Response({"error": "The AI service is currently experiencing high load. Please try again in a moment."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            elif "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                return Response({"error": "AI rate limit exceeded. Please wait a minute and try again."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            return Response({"error": f"Failed to generate cover letter: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InterviewEvaluationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        question = request.data.get("question")
        answer = request.data.get("answer")

        if not question or not answer:
            return Response({"error": "Question and answer are required."}, status=status.HTTP_400_BAD_REQUEST)

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return Response({"error": "LLM API Key missing. Ensure you have GOOGLE_API_KEY set."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", google_api_key=api_key, temperature=0.7)
        
        prompt = f"""
        You are an expert technical interviewer evaluating a candidate's answer.
        
        Question: {question}
        Candidate's Answer: {answer}
        
        Evaluate the candidate's answer. Provide concise, constructive feedback (2-3 sentences). 
        Identify what was good, what was missing, and give a rating out of 10.
        Format your response nicely.
        """
        
        analysis_id = request.data.get("analysis_id")
        
        try:
            response = llm.invoke(prompt)
            feedback = response.content
            if isinstance(feedback, list):
                feedback = "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in feedback])
                
            if analysis_id:
                try:
                    # Update the ResumeAnalysis record with the feedback
                    analysis = ResumeAnalysis.objects.get(id=analysis_id, user=request.user)
                    if not isinstance(analysis.interview_feedbacks, dict):
                        analysis.interview_feedbacks = {}
                    
                    # Store both answer and feedback, keyed by the question text
                    analysis.interview_feedbacks[question] = {
                        "answer": answer,
                        "feedback": feedback
                    }
                    analysis.save(update_fields=['interview_feedbacks'])
                except ResumeAnalysis.DoesNotExist:
                    pass # Silently ignore if not found
                    
            return Response({"feedback": feedback}, status=status.HTTP_200_OK)
        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "unavailable" in error_str:
                return Response({"error": "The AI service is currently experiencing high load. Please try again in a moment."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            elif "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                return Response({"error": "AI rate limit exceeded. Please wait a minute and try again."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            return Response({"error": f"Failed to evaluate answer: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

