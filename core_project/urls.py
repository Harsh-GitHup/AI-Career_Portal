from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This automatically imports all API endpoints from career_app/urls.py
    path('api/', include('career_app.urls')),
]