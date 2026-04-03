from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/test-message/", views.test_message, name="test-message"),
    path("check-enrollment/", views.check_enrollment, name="check_enrollment"),
    path("class-rosters/", views.class_rosters, name="class_rosters"),
    path("student/<str:student_id>/", views.student_detail, name="student_detail"),
    path("teacher/<int:teacher_id>/", views.teacher_profile, name="teacher_profile"),
    
    path("portal/login/", views.portal_login, name="portal_login"),
    path("portal/register/", views.portal_register, name="portal_register"),
    path("portal/logout/", views.portal_logout, name="portal_logout"),
    path("portal/dashboard/", views.portal_dashboard, name="portal_dashboard"),
    
    # ໜ້າປະເມີນຜົນການຮຽນຮູ້ (Learning Assessment)
    path("assessment/", views.learning_assessment, name="learning_assessment"),
]
