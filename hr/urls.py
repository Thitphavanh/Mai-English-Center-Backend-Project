from django.urls import path
from . import views

app_name = "hr"

urlpatterns = [
    path("add-employee/", views.add_employee, name="add_employee"),
    path("timesheet/", views.timesheet_list, name="timesheet_list"),
    path("payroll-report/", views.monthly_payroll_report, name="payroll_report"),
    path("update-timesheet/", views.update_timesheet, name="update_timesheet"),
    path("batch-update-timesheet/", views.batch_update_timesheet, name="batch_update_timesheet"),
]
