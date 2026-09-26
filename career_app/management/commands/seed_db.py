from django.core.management.base import BaseCommand
from career_app.models import CareerRole, RoleSkill, CourseRecommendation, InterviewQuestion

class Command(BaseCommand):
    help = 'Seeds the database with essential Career Roles, Skills, Courses, and Questions'

    def handle(self, *args, **kwargs):
        # Data Scientist
        ds, _ = CareerRole.objects.get_or_create(title="Data Scientist")
        skills_ds = ["Python", "Machine Learning", "SQL", "Data Analysis", "Deep Learning"]
        for s in skills_ds:
            RoleSkill.objects.get_or_create(role=ds, skill_name=s)
            CourseRecommendation.objects.get_or_create(skill_name=s, defaults={
                'provider': 'Coursera / NPTEL',
                'course_title': f'Advanced {s} Specialization'
            })
        
        qs_ds = [
            "Explain the bias-variance tradeoff.",
            "How do you handle missing data in a dataset?",
            "Describe a time you used machine learning to solve a real problem.",
            "What is the difference between supervised and unsupervised learning?",
            "How do you evaluate a model's performance?"
        ]
        for q in qs_ds:
            InterviewQuestion.objects.get_or_create(role=ds, question_text=q)

        # Software Engineer
        se, _ = CareerRole.objects.get_or_create(title="Software Engineer")
        skills_se = ["Python", "Java", "React", "Docker", "Algorithms", "Git"]
        for s in skills_se:
            RoleSkill.objects.get_or_create(role=se, skill_name=s)
            CourseRecommendation.objects.get_or_create(skill_name=s, defaults={
                'provider': 'Udemy / SWAYAM',
                'course_title': f'Mastering {s}'
            })
            
        qs_se = [
            "What is the difference between a process and a thread?",
            "Explain how you would design a URL shortener.",
            "Describe your experience with CI/CD pipelines.",
            "How do you handle merge conflicts in Git?",
            "What are the SOLID principles?"
        ]
        for q in qs_se:
            InterviewQuestion.objects.get_or_create(role=se, question_text=q)
            
        # Data Analyst
        da, _ = CareerRole.objects.get_or_create(title="Data Analyst")
        skills_da = ["SQL", "Excel", "Tableau", "PowerBI", "Python"]
        for s in skills_da:
            RoleSkill.objects.get_or_create(role=da, skill_name=s)
            CourseRecommendation.objects.get_or_create(skill_name=s, defaults={
                'provider': 'Google / NPTEL',
                'course_title': f'{s} for Data Analysts'
            })
            
        qs_da = [
            "How do you perform a JOIN in SQL?",
            "Explain a complex dashboard you built.",
            "How do you handle outliers in data?",
            "What is a pivot table?",
            "Describe your experience with data cleaning."
        ]
        for q in qs_da:
            InterviewQuestion.objects.get_or_create(role=da, question_text=q)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
