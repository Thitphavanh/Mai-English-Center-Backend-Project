from django import template
from django.db.models import Sum
from academics.models import Student, Course, ClassSchedule, Enrollment
from hr.models import EmployeeProfile, Timesheet, PayrollSummary
import datetime
from django.utils import timezone

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    active_schedules = ClassSchedule.objects.filter(is_active=True).count()
    total_enrollments = Enrollment.objects.count()

    total_employees = EmployeeProfile.objects.count()

    # Timesheets for this month
    monthly_timesheets = Timesheet.objects.filter(date__year=current_year, date__month=current_month)
    total_hours_this_month = monthly_timesheets.aggregate(total=Sum('hours_worked'))['total'] or 0

    return {
        'total_students': total_students,
        'total_courses': total_courses,
        'active_schedules': active_schedules,
        'total_enrollments': total_enrollments,
        'total_employees': total_employees,
        'total_hours_this_month': total_hours_this_month,
    }
