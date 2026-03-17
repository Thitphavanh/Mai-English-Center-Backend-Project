from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    # path("", views.index, name="index"),
    path("api/test-message/", views.test_message, name="test-message"),
]
