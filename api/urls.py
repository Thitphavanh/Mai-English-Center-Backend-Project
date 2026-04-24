from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("test-message/", views.test_message, name="test-message"),
    path("portal/login/", views.api_portal_login, name="api_portal_login"),
    path("portal/dashboard/", views.api_portal_dashboard, name="api_portal_dashboard"),
    path("teacher/<int:teacher_id>/", views.api_teacher_profile, name="api_teacher_profile"),
    path("home-data/", views.api_home_data, name="api_home_data"),
    path("course/<slug:slug>/", views.api_course_detail, name="api_course_detail"),
    path("courses/", views.api_course_list, name="api_course_list"),
    path("popups/", views.api_get_popups, name="api_get_popups"),
]
