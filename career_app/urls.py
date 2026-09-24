from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UploadResumeAPIView,
    OpportunityListAPIView,
    RecommendedMatchesAPIView,
    SocialLoginAPIView,
    ChatbotAPIView,
    StudentProfileViewSet,
    AcademicRecordViewSet
)

router = DefaultRouter()
router.register(r'profiles', StudentProfileViewSet, basename='profile')
router.register(r'academics', AcademicRecordViewSet, basename='academic')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-resume/', UploadResumeAPIView.as_view(), name='api_upload_resume'),
    path('opportunities/', OpportunityListAPIView.as_view(), name='api_opportunities'),
    path('recommendations/<int:profile_id>/', RecommendedMatchesAPIView.as_view(), name='api_recommendations'),
    path('social-login/', SocialLoginAPIView.as_view(), name='api_social_login'),
    path('chatbot/', ChatbotAPIView.as_view(), name='api_chatbot'),
]