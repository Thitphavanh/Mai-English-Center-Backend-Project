from django.urls import path
from . import views

app_name = "academics"

urlpatterns = [
    path("tuition/", views.tuition_list, name="tuition_list"),
    path("tuition-report/", views.class_tuition_report, name="class_tuition_report"),
    path("student-count/", views.weekly_student_summary, name="student_count"),
]
