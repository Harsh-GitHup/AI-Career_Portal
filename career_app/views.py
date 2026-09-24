import traceback
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Opportunity, ProfileMatch, StudentProfile, AcademicRecord
from .serializers import OpportunitySerializer, ProfileMatchSerializer, StudentProfileSerializer, AcademicRecordSerializer
from .ml_pipeline import analyze_resume
from .tasks import calculate_matches_for_profile, run_govt_schemes_scraper, run_courses_scraper, run_universal_scraper
from langchain_google_genai import ChatGoogleGenerativeAI
from django.contrib.auth import login
from django.contrib.auth.models import User
import os
from rest_framework import viewsets

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

class AcademicRecordViewSet(viewsets.ModelViewSet):
    queryset = AcademicRecord.objects.all()
    serializer_class = AcademicRecordSerializer


@method_decorator(csrf_exempt, name='dispatch')
class UploadResumeAPIView(APIView):
    """Parses resume PDF, stores profile in MySQL, and queues match scoring."""
    def post(self, request, *args, **kwargs):
        resume_file = request.FILES.get('resume')
        if not resume_file:
            return Response({"error": "No PDF file supplied."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. AI Parsing Pipeline
            analysis = analyze_resume(resume_file.read())

            # 2. Persist to MySQL
            if request.user.is_authenticated:
                profile, _ = StudentProfile.objects.get_or_create(user=request.user)
            else:
                profile = StudentProfile.objects.create(full_name=analysis.full_name)

            profile.target_role = analysis.target_professions[0] if analysis.target_professions else "Junior Analyst"
            profile.current_skills = analysis.extracted_skills
            profile.skill_gaps = analysis.skill_gaps
            profile.resume_improvements = analysis.resume_improvements
            profile.interview_questions = analysis.interview_questions
            
            # Dynamic Readiness Calculation
            penalty = len(analysis.skill_gaps) * 8
            profile.readiness_score = max(35, 100 - penalty)
            profile.save()

            # 3. Synchronously ensure baseline opportunities exist
            if Opportunity.objects.count() == 0:
                run_govt_schemes_scraper()
                run_courses_scraper()

            # 4. Trigger Celery Asynchronous Match Engine & Scrapers
            run_universal_scraper.delay(profile.id)
            calculate_matches_for_profile.delay(profile.id)

            return Response({
                "profile_id": profile.id,
                "full_name": profile.full_name,
                "target_role": profile.target_role,
                "readiness_score": profile.readiness_score,
                "extracted_skills": profile.current_skills,
                "skill_gaps": profile.skill_gaps,
                "recommended_courses": analysis.recommended_courses,
                "resume_improvements": profile.resume_improvements,
                "interview_questions": profile.interview_questions
            }, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OpportunityListAPIView(generics.ListAPIView):
    """Search and filter catalog of opportunities."""
    queryset = Opportunity.objects.filter(is_active=True)
    serializer_class = OpportunitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'provider', 'description', 'required_skills__skill_name']
    ordering_fields = ['created_at', 'title', 'deadline']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        opp_type = self.request.query_params.get('type')
        is_free = self.request.query_params.get('is_free')

        if opp_type:
            qs = qs.filter(opportunity_type=opp_type)
        if is_free is not None:
            qs = qs.filter(is_free=(is_free.lower() == 'true'))
        return qs.distinct()


class RecommendedMatchesAPIView(APIView):
    """Retrieves ranked opportunities for a specific profile ID."""
    def get(self, request, profile_id, *args, **kwargs):
        matches = ProfileMatch.objects.filter(profile_id=profile_id).select_related('opportunity')
        
        # Categorize matches for the frontend
        schemes = [m for m in matches if m.opportunity.opportunity_type == 'Scheme']
        others = [m for m in matches if m.opportunity.opportunity_type != 'Scheme']

        return Response({
            "schemes": ProfileMatchSerializer(schemes, many=True).data,
            "opportunities": ProfileMatchSerializer(others, many=True).data
        })

@method_decorator(csrf_exempt, name='dispatch')
class SocialLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # A simple mocked social login view for the sake of completeness
        email = request.data.get('email')
        name = request.data.get('name', 'Student')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        user, created = User.objects.get_or_create(username=email, defaults={'email': email, 'first_name': name})
        login(request, user)
        return Response({"message": "Successfully logged in", "user_id": user.id})

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotAPIView(APIView):
    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        profile_id = request.data.get('profile_id')
        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        context = "You are a helpful CareerAI chatbot."
        if profile_id:
            try:
                profile = StudentProfile.objects.get(id=profile_id)
                context += f"\nThe user is a {profile.target_role} with skills: {', '.join(profile.current_skills)}."
            except StudentProfile.DoesNotExist:
                pass
                
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=api_key, temperature=0.7)
            try:
                response = llm.invoke(f"{context}\n\nUser: {message}\nAI:")
                ai_text = response.content
            except Exception as e:
                ai_text = "Sorry, I am facing an issue right now."
        else:
            ai_text = "I'm sorry, my AI backend is not configured."

        return Response({"response": ai_text})