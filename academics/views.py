from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from .models import TuitionFee, Enrollment, ClassSchedule
from .forms import TuitionFeeForm

def tuition_list(request):
    """ View to handle Tuition Fees tracking """
    fees = TuitionFee.objects.select_related('enrollment__student').all()[:50]
    
    if request.method == 'POST':
        form = TuitionFeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tuition Fee record added!')
            return redirect('academics:tuition_list')
    else:
        form = TuitionFeeForm()
        
    context = {'fees': fees, 'form': form}
    return render(request, 'academics/tuition.html', context)


def weekly_student_summary(request):
    """ ສະຫຼຸບຈຳນວນນັກຮຽນປະຈຳອາທິດ """
    # Group enrollments by Class Schedule
    classes_summary = ClassSchedule.objects.annotate(
        total_students=Count('enrollments')
    ).prefetch_related('enrollments__student')
    
    context = {'classes_summary': classes_summary}
    return render(request, 'academics/student_count.html', context)


def class_tuition_report(request):
    """ View for specific class tuition fee report in the format of the Excel sheet """
    # Mocking data specifically for demonstration, in reality this queries TuitionFee by ClassSchedule
    month_query = request.GET.get('month', '03/2026')
    class_id = request.GET.get('class_id')
    
    enrollments = Enrollment.objects.select_related('student', 'class_schedule').prefetch_related('tuition_fees')
    if class_id:
        enrollments = enrollments.filter(class_schedule_id=class_id)
        
    context = {
        'enrollments': enrollments,
        'current_month': month_query
    }
    return render(request, 'academics/tuition_class_report.html', context)

