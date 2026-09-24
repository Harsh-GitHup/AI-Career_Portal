from rest_framework import serializers
from .models import Opportunity, ProfileMatch, StudentProfile, AcademicRecord

class OpportunitySerializer(serializers.ModelSerializer):
    required_skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='skill_name'
    )

    class Meta:
        model = Opportunity
        fields = [
            'id', 'title', 'provider', 'opportunity_type', 'is_free',
            'stipend_or_cost', 'mode', 'location', 'deadline', 'url',
            'description', 'eligibility', 'required_skills'
        ]

class ProfileMatchSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)

    class Meta:
        model = ProfileMatch
        fields = ['id', 'relevance_score', 'matching_skills', 'reasoning', 'is_bookmarked', 'opportunity']

class AcademicRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicRecord
        fields = ['id', 'degree', 'institution', 'graduation_year', 'cgpa']

class StudentProfileSerializer(serializers.ModelSerializer):
    academics = AcademicRecordSerializer(many=True, read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'bio', 'target_role',
            'current_skills', 'skill_gaps', 'resume_improvements', 'interview_questions',
            'readiness_score', 'employability_score', 'academics'
        ]