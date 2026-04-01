import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from academics.models import *

student = Student.objects.filter(nick_name__icontains="ແມວ").first()
if student:
    enrollment = student.enrollments.first()
    if enrollment:
        assessment = Assessment.objects.filter(enrollment=enrollment).last()
        if assessment:
            assessment.gpa = 3.8
            assessment.save()
            print("Successfully updated GPA to 3.8 for Meow!")
        else:
            print("No assessment found")
    else:
        print("No enrollment found")
else:
    print("No student found")
