from django.urls import path
from . import views
from academics.views_monthly_score import (
    MonthlyScoreCalendarView,
    MonthlyScoreBulkEntryView,
    MonthlyScoreDetailView,
)

app_name = 'backoffice'

def generate_crud_urls(model_name, list_view, create_view, update_view, delete_view):
    return [
        path(f'{model_name}s/', list_view.as_view(), name=f'{model_name}-list'),
        path(f'{model_name}s/add/', create_view.as_view(), name=f'{model_name}-add'),
        path(f'{model_name}s/<int:pk>/edit/', update_view.as_view(), name=f'{model_name}-edit'),
        path(f'{model_name}s/<int:pk>/delete/', delete_view.as_view(), name=f'{model_name}-delete'),
    ]

urlpatterns = [
    path('login/', views.backoffice_login, name='login'),
    path('register/', views.backoffice_register, name='register'),
    path('logout/', views.backoffice_logout, name='logout'),
    path('', views.SystemSelectionView.as_view(), name='system-selection'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]

# ACADEMICS
urlpatterns += generate_crud_urls('course', views.CourseList, views.CourseCreate, views.CourseUpdate, views.CourseDelete)
urlpatterns += generate_crud_urls('classschedule', views.ClassScheduleList, views.ClassScheduleCreate, views.ClassScheduleUpdate, views.ClassScheduleDelete)
urlpatterns += generate_crud_urls('student', views.StudentList, views.StudentCreate, views.StudentUpdate, views.StudentDelete)
urlpatterns += generate_crud_urls('enrollment', views.EnrollmentList, views.EnrollmentCreate, views.EnrollmentUpdate, views.EnrollmentDelete)
urlpatterns += generate_crud_urls('dailychecklist', views.DailyChecklistList, views.DailyChecklistCreate, views.DailyChecklistUpdate, views.DailyChecklistDelete)
urlpatterns += generate_crud_urls('assessment', views.AssessmentList, views.AssessmentCreate, views.AssessmentUpdate, views.AssessmentDelete)
urlpatterns += generate_crud_urls('assessmentcriteria', views.AssessmentCriteriaList, views.AssessmentCriteriaCreate, views.AssessmentCriteriaUpdate, views.AssessmentCriteriaDelete)
urlpatterns += generate_crud_urls('tuitionfee', views.TuitionFeeList, views.TuitionFeeCreate, views.TuitionFeeUpdate, views.TuitionFeeDelete)

# HR
urlpatterns += generate_crud_urls('employeeprofile', views.EmployeeProfileList, views.EmployeeProfileCreate, views.EmployeeProfileUpdate, views.EmployeeProfileDelete)
urlpatterns += generate_crud_urls('hourlyraterole', views.HourlyRateRoleList, views.HourlyRateRoleCreate, views.HourlyRateRoleUpdate, views.HourlyRateRoleDelete)
urlpatterns += generate_crud_urls('timesheet', views.TimesheetList, views.TimesheetCreate, views.TimesheetUpdate, views.TimesheetDelete)
urlpatterns += generate_crud_urls('payrollsummary', views.PayrollSummaryList, views.PayrollSummaryCreate, views.PayrollSummaryUpdate, views.PayrollSummaryDelete)

# AUTH
urlpatterns += generate_crud_urls('user', views.UserList, views.UserCreate, views.UserUpdate, views.UserDelete)
urlpatterns += generate_crud_urls('group', views.GroupList, views.GroupCreate, views.GroupUpdate, views.GroupDelete)

# MONTHLY SCORES
urlpatterns += [
    path('monthly-scores/', MonthlyScoreCalendarView.as_view(), name='monthlyscore-calendar'),
    path('monthly-scores/entry/', MonthlyScoreBulkEntryView.as_view(), name='monthlyscore-entry'),
    path('monthly-scores/detail/', MonthlyScoreDetailView.as_view(), name='monthlyscore-detail'),
]

# TEMPLATES & DOCUMENTS (ບິນ ແລະ ບັດ)
urlpatterns += [
    path('tuition-invoice/<int:pk>/', views.TuitionInvoiceView.as_view(), name='tuition-invoice'),
    path('student-id-card/<int:pk>/', views.StudentIDCardView.as_view(), name='student-id-card'),
]

# ATTENDANCE (Teacher & Student)
urlpatterns += [
    path('attendance/', views.AttendancePortalView.as_view(), name='attendance-portal'),
]

# CHECKLIST GRID (ໝາຍຊື່ນັກຮຽນແບບຕາຕະລາງ)
urlpatterns += [
    path('checklist-grid/', views.checklist_grid_view, name='checklist-grid'),
    path('api/update-checklist/', views.update_checklist, name='update-checklist'),
    path('api/batch-update-checklist/', views.batch_update_checklist, name='batch-update-checklist'),
]
