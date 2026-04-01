from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Timesheet, EmployeeProfile
from .forms import TimesheetForm, EmployeeProfileWebForm

@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeProfileWebForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'ເພີ່ມສະມາຊິກໃໝ່ສຳເລັດແລ້ວ!')
            return redirect('hr:payroll_report')
    else:
        form = EmployeeProfileWebForm()
        
    return render(request, 'hr/add_employee.html', {'form': form})


def timesheet_list(request):
    """
    Views to list and create employee timesheets.
    """
    timesheets = Timesheet.objects.select_related('employee__user').all()[:50]
    
    if request.method == 'POST':
        form = TimesheetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timesheet saved successfully!')
            return redirect('hr:timesheet_list')
    else:
        form = TimesheetForm()
        
    context = {
        'timesheets': timesheets,
        'form': form
    }
    return render(request, 'hr/timesheet.html', context)

def monthly_payroll_report(request):
    import datetime
    from calendar import monthrange
    from django.db.models import Q
    from .models import EmployeeProfile, Timesheet
    
    month_query = request.GET.get('month', '11')
    year_query = request.GET.get('year', '2025')
    search_query = request.GET.get('search', '').strip()
    
    try:
        month_int = int(month_query)
        year_int = int(year_query)
        _, num_days = monthrange(year_int, month_int)
    except:
        month_int, year_int, num_days = 11, 2025, 30

    employees = EmployeeProfile.objects.select_related('user', 'role').all()

    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Pre-fetch timesheets
    timesheets = Timesheet.objects.filter(
        date__year=year_int, date__month=month_int, employee__in=employees
    )
    
    ts_dict = {}
    for ts in timesheets:
        if ts.employee_id not in ts_dict:
            ts_dict[ts.employee_id] = {}
        ts_dict[ts.employee_id][ts.date.day] = float(ts.hours_worked)
        
    payroll_data = []
    grand_total_amount = 0
    days_range = list(range(1, num_days + 1))
    
    for emp in employees:
        emp_times = ts_dict.get(emp.id, {})
        daily_hours = [emp_times.get(day, "") for day in days_range]
        total_hours = sum(filter(None, daily_hours))
        
        rate = emp.role.rate_per_hour if emp.role else 80000 # Default if no role is set
        total_amount = float(total_hours) * float(rate)
        grand_total_amount += total_amount
        
        payroll_data.append({
            'employee': emp,
            'daily_hours': daily_hours,
            'total_hours': total_hours,
            'total_amount': total_amount,
            'total_amount_formatted': "{:,.0f}".format(total_amount)
        })
        
    context = {
        'search_query': search_query,
        'month': f"{month_int:02d}",
        'year': str(year_int),
        'month_year': f"{month_int:02d}/{year_int}",
        'days_range': days_range,
        'payroll_data': payroll_data,
        'grand_total_amount': grand_total_amount,
        'grand_total_amount_formatted': "{:,.0f}".format(grand_total_amount),
    }
    return render(request, 'hr/payroll_monthly.html', context)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from datetime import date

@require_POST
def update_timesheet(request):
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        hours = data.get('hours')
        
        target_date = date(year, month, day)
        
        if hours and str(hours).strip():
            hours_float = float(hours)
            if hours_float > 0:
                Timesheet.objects.update_or_create(
                    employee_id=employee_id,
                    date=target_date,
                    defaults={'hours_worked': hours_float}
                )
            else:
                Timesheet.objects.filter(employee_id=employee_id, date=target_date).delete()
        else:
            # If hours is empty, delete the record
            Timesheet.objects.filter(employee_id=employee_id, date=target_date).delete()
            
        return JsonResponse({'status': 'success', 'message': 'Timesheet updated'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def batch_update_timesheet(request):
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        year = int(data.get('year'))
        month = int(data.get('month'))
        updates = data.get('updates', [])
        
        for upd in updates:
            day = int(upd.get('day'))
            hours = upd.get('hours')
            target_date = date(year, month, day)
            
            if hours and str(hours).strip():
                hours_float = float(hours)
                if hours_float > 0:
                    Timesheet.objects.update_or_create(
                        employee_id=employee_id,
                        date=target_date,
                        defaults={'hours_worked': hours_float}
                    )
                else:
                    Timesheet.objects.filter(employee_id=employee_id, date=target_date).delete()
            else:
                Timesheet.objects.filter(employee_id=employee_id, date=target_date).delete()
                
        return JsonResponse({'status': 'success', 'message': 'Batch timesheet updated'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
