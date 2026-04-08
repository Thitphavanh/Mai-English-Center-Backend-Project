import types
from django import forms
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
        
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # If they are logged in but not a staff, redirect to portal
            return redirect('home:portal_dashboard')
        return redirect('backoffice:login')
from django.contrib.auth.models import User, Group
from academics.models import Course, ClassSchedule, Student, Enrollment, DailyChecklist, Assessment, AssessmentCriteria, TuitionFee
from hr.models import EmployeeProfile, HourlyRateRole, Timesheet, PayrollSummary
from hr.admin import EmployeeProfileForm
from django.contrib.auth import authenticate, login, logout

def backoffice_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('backoffice:dashboard')
    error = None
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('backoffice:dashboard')
            else:
                error = "ບັນຊີນີ້ບໍ່ມີສິດເຂົ້າເຖິງລະບົບຫຼັງບ້ານ (Not a Staff account)."
        else:
            error = "ຊື່ຜູ້ໃຊ້ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ (Invalid credentials)."
    return render(request, 'backoffice/login.html', {'error': error})

def backoffice_register(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('backoffice:dashboard')
    error = None
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        fn = request.POST.get('first_name')
        if User.objects.filter(username=u).exists():
            error = "ຊື່ຜູ້ໃຊ້ນີ້ມີຄົນໃຊ້ແລ້ວ (Username already exists)."
        else:
            user = User.objects.create_user(username=u, password=p, first_name=fn, is_staff=True)
            login(request, user)
            return redirect('backoffice:dashboard')
    return render(request, 'backoffice/register.html', {'error': error})

def backoffice_logout(request):
    logout(request)
    return redirect('backoffice:login')

class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "backoffice/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_students'] = Student.objects.count()
        context['total_courses'] = Course.objects.count()
        context['total_employees'] = EmployeeProfile.objects.count()
        return context

# Generic Base Views designed to save time and code
class BaseGenericListView(StaffRequiredMixin, ListView):
    template_name = "backoffice/generic_list.html"
    list_display = []
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Filter Students by Class Schedule if provided
        if self.model.__name__ == 'Student':
            cs_id = self.request.GET.get('class_schedule')
            if cs_id:
                qs = qs.filter(enrollments__class_schedule_id=cs_id).distinct()
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        headers = []
        for f in self.list_display:
            try:
                headers.append(self.model._meta.get_field(f).verbose_name.title())
            except:
                headers.append(f.title().replace('_', ' '))
                
        rows = []
        for obj in context['object_list']:
            row = []
            for f in self.list_display:
                val = getattr(obj, f)
                # If the value is a User object, show full name if available
                if isinstance(val, User):
                    full_name = val.get_full_name()
                    val = full_name if full_name.strip() else val.username
                    
                row.append(str(val) if val is not None else '')
            rows.append({'pk': obj.pk, 'cells': row})
            
        context['headers'] = headers
        context['rows'] = rows
        context['title'] = self.model._meta.verbose_name_plural.title()
        context['model_name'] = self.model.__name__
        
        # Inject context for Student list filter dropdown
        if self.model.__name__ == 'Student':
            from academics.models import ClassSchedule
            context['class_schedules'] = ClassSchedule.objects.select_related('course', 'teacher').all()
            context['current_schedule_id'] = str(self.request.GET.get('class_schedule', ''))
            context['is_student_list'] = True
        
        model_name = self.model.__name__.lower()
        context['add_url'] = reverse_lazy(f'backoffice:{model_name}-add')
        context['edit_url_name'] = f'backoffice:{model_name}-edit'
        context['delete_url_name'] = f'backoffice:{model_name}-delete'
        return context

class CustomUserSelectFixMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            if hasattr(field, 'queryset') and field.queryset.model == User:
                if field_name in ['teacher', 'evaluator']:
                    field.queryset = field.queryset.filter(is_staff=True)
                elif field_name == 'parent':
                    field.queryset = field.queryset.filter(is_staff=False)
                    field.help_text = "ລາຍຊື່ຜູ້ປົກຄອງ (ຖ້າບໍ່ມີ ລົບກວນໄປສ້າງບັນຊີໃໝ່ໃນເມນູ Users ໃຫ້ພໍ່ແມ່ກ່ອນ ໂດຍປົດຕິກ staff ຖິ້ມ)"
                    
                field.label_from_instance = lambda obj: obj.get_full_name() if obj.get_full_name().strip() else obj.username
                
            # Convert month and month_year to dropdowns
            if field_name in ['month', 'month_year']:
                import datetime
                today = datetime.date.today()
                month_choices = [('', '--- ເລືອກເດືອນ ---')]
                
                model = getattr(getattr(form, 'Meta', None), 'model', None)
                if not model and hasattr(form, '_meta'):
                    model = getattr(form._meta, 'model', None)
                
                existing_months = []
                if model:
                    existing_months = list(model.objects.exclude(**{f"{field_name}__isnull": True}).exclude(**{field_name: ''}).values_list(field_name, flat=True).distinct())
                
                generated_months = []
                for i in range(-12, 13):
                    m = today.month + i - 1
                    y = today.year + m // 12
                    m = m % 12 + 1
                    dt = datetime.date(y, m, 1)
                    m_str = dt.strftime('%m/%Y')
                    m_label = dt.strftime('%b %Y') + f' ({m_str})'
                    generated_months.append((m_str, m_label))
                    
                gen_keys = [k for k,v in generated_months]
                for em in existing_months:
                    if em not in gen_keys:
                        month_choices.append((em, em))
                
                month_choices.extend(generated_months)
                
                form.fields[field_name] = forms.ChoiceField(
                    choices=month_choices,
                    required=field.required,
                    label=field.label,
                    initial=today.strftime('%m/%Y') if not getattr(form.instance, 'pk', None) else field.initial
                )

            # Convert Amount to dropdown
            if field_name == 'amount':
                model = getattr(getattr(form, 'Meta', None), 'model', None)
                if not model and hasattr(form, '_meta'):
                    model = getattr(form._meta, 'model', None)
                    
                existing_amounts = []
                if model:
                    existing_amounts = list(model.objects.exclude(amount__isnull=True).values_list('amount', flat=True).distinct())
                    
                default_amounts = [
                    500000, 600000, 700000, 800000, 900000, 1000000, 1200000, 1500000
                ]
                
                all_amounts = set([int(x) for x in existing_amounts] + default_amounts)
                choices = [('', '--- ເລືອກຈຳນວນເງິນ ---')] + [(str(a), f"{a:,.0f} LAK") for a in sorted(all_amounts)]
                
                form.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    required=field.required,
                    label=field.label,
                    initial=field.initial
                )
                
            # Auto-fill next student_id (Running Number) if not already set
            if field_name == 'student_id' and not getattr(form.instance, 'pk', None):
                model = getattr(getattr(form, 'Meta', None), 'model', None)
                if not model and hasattr(form, '_meta'):
                    model = getattr(form._meta, 'model', None)
                    
                if model and model.__name__ == 'Student':
                    last_student = model.objects.filter(student_id__regex=r'^\d+$').order_by('-student_id').first()
                    if last_student and last_student.student_id:
                        next_id = int(last_student.student_id) + 1
                        field.initial = f"{next_id:05d}"
                    else:
                        field.initial = "00001"
                        
            # Enable HTML5 date picker for Date fields
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={'type': 'date'})
                
            # Change time_slot to a dynamic selectable dropdown
            if field_name == 'time_slot':
                model = getattr(getattr(form, 'Meta', None), 'model', None)
                if not model and hasattr(form, '_meta'):
                    model = getattr(form._meta, 'model', None)
                    
                existing_slots = []
                if model:
                    existing_slots = list(model.objects.exclude(time_slot__isnull=True).exclude(time_slot='').values_list('time_slot', flat=True).distinct())
                    
                default_slots = [
                    '04:30 - 05:30 PM', '05:00 - 06:00 PM', '05:30 - 06:30 PM',
                    '06:00 - 07:00 PM', '06:30 - 07:30 PM', '07:00 - 08:00 PM', '07:30 - 08:30 PM',
                    '08:00 - 10:00 AM', '10:00 - 12:00 AM', '01:00 - 03:00 PM'
                ]
                
                for ds in default_slots:
                    if ds not in existing_slots:
                        existing_slots.append(ds)
                
                choices = [('', '--- ເລືອກເວລາຮຽນ ---')] + [(s, s) for s in sorted(existing_slots)]
                
                form.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    required=field.required,
                    label=field.label,
                    help_text=field.help_text,
                    initial=field.initial
                )
                
        return form

class BaseGenericCreateView(StaffRequiredMixin, CustomUserSelectFixMixin, CreateView):
    template_name = "backoffice/form.html"
    
    def get_success_url(self):
        return reverse_lazy(f'backoffice:{self.model.__name__.lower()}-list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Add {self.model._meta.verbose_name.title()}"
        context['back_url'] = self.get_success_url()
        return context

class BaseGenericUpdateView(StaffRequiredMixin, CustomUserSelectFixMixin, UpdateView):
    template_name = "backoffice/form.html"
    
    def get_success_url(self):
        return reverse_lazy(f'backoffice:{self.model.__name__.lower()}-list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit {self.model._meta.verbose_name.title()}: {self.object}"
        context['back_url'] = self.get_success_url()
        return context

class BaseGenericDeleteView(StaffRequiredMixin, DeleteView):
    template_name = "backoffice/confirm_delete.html"
    def get_success_url(self):
        return reverse_lazy(f'backoffice:{self.model.__name__.lower()}-list')


def create_crud_views(model_class, display_fields, form_class=None):
    """Automatically build the 4 CRUD views for a given model"""
    model_name = model_class.__name__
    
    # 1. LIST
    ListViewCls = type(f"{model_name}ListView", (BaseGenericListView,), {
        'model': model_class,
        'list_display': display_fields
    })
    
    # 2. CREATE
    if form_class:
        CreateViewCls = type(f"{model_name}CreateView", (BaseGenericCreateView,), {
            'model': model_class,
            'form_class': form_class
        })
        UpdateViewCls = type(f"{model_name}UpdateView", (BaseGenericUpdateView,), {
            'model': model_class,
            'form_class': form_class
        })
    else:
        CreateViewCls = type(f"{model_name}CreateView", (BaseGenericCreateView,), {
            'model': model_class,
            'fields': '__all__'
        })
        UpdateViewCls = type(f"{model_name}UpdateView", (BaseGenericUpdateView,), {
            'model': model_class,
            'fields': '__all__'
        })
        
    # 4. DELETE
    DeleteViewCls = type(f"{model_name}DeleteView", (BaseGenericDeleteView,), {
        'model': model_class
    })
    
    return ListViewCls, CreateViewCls, UpdateViewCls, DeleteViewCls

# ACADEMICS
CourseList, CourseCreate, CourseUpdate, CourseDelete = create_crud_views(Course, ['name', 'book_name'])
ClassScheduleList, ClassScheduleCreate, ClassScheduleUpdate, ClassScheduleDelete = create_crud_views(ClassSchedule, ['course', 'time_slot', 'teacher', 'is_active'])
StudentList, StudentCreate, StudentUpdate, StudentDelete = create_crud_views(Student, ['student_id', 'full_name', 'phone_number'])
EnrollmentList, EnrollmentCreate, EnrollmentUpdate, EnrollmentDelete = create_crud_views(Enrollment, ['student', 'class_schedule', 'enrollment_date'])
DailyChecklistList, DailyChecklistCreate, DailyChecklistUpdate, DailyChecklistDelete = create_crud_views(DailyChecklist, ['enrollment', 'date', 'status'])
AssessmentList, AssessmentCreate, AssessmentUpdate, AssessmentDelete = create_crud_views(Assessment, ['enrollment', 'total_score', 'gpa'])
AssessmentCriteriaList, AssessmentCriteriaCreate, AssessmentCriteriaUpdate, AssessmentCriteriaDelete = create_crud_views(AssessmentCriteria, ['name_en', 'name_lo', 'category'])
TuitionFeeList, TuitionFeeCreate, TuitionFeeUpdate, TuitionFeeDelete = create_crud_views(TuitionFee, ['enrollment', 'month', 'amount', 'status'])

# HR
EmployeeProfileList, EmployeeProfileCreate, EmployeeProfileUpdate, EmployeeProfileDelete = create_crud_views(EmployeeProfile, ['user', 'phone_number', 'role'], form_class=EmployeeProfileForm)
HourlyRateRoleList, HourlyRateRoleCreate, HourlyRateRoleUpdate, HourlyRateRoleDelete = create_crud_views(HourlyRateRole, ['name', 'rate_per_hour'])
TimesheetList, TimesheetCreate, TimesheetUpdate, TimesheetDelete = create_crud_views(Timesheet, ['employee', 'date', 'hours_worked'])
PayrollSummaryList, PayrollSummaryCreate, PayrollSummaryUpdate, PayrollSummaryDelete = create_crud_views(PayrollSummary, ['employee', 'month_year', 'total_amount', 'is_paid'])

# AUTH
UserList, UserCreate, UserUpdate, UserDelete = create_crud_views(User, ['username', 'first_name', 'last_name', 'email', 'is_staff'])
GroupList, GroupCreate, GroupUpdate, GroupDelete = create_crud_views(Group, ['name'])
# TEMPLATES & DOCUMENTS
class TuitionInvoiceView(StaffRequiredMixin, TemplateView):
    template_name = "backoffice/templates/tuition_invoice.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = TuitionFee.objects.select_related('enrollment__student', 'enrollment__class_schedule').get(pk=self.kwargs['pk'])
        return context

class StudentIDCardView(StaffRequiredMixin, TemplateView):
    template_name = "backoffice/templates/student_id_card.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = Student.objects.get(pk=self.kwargs['pk'])
        return context

class AttendancePortalView(StaffRequiredMixin, TemplateView):
    template_name = "backoffice/templates/attendance_portal.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import datetime
        date_str = self.request.GET.get('date', datetime.date.today().isoformat())
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            selected_date = datetime.date.today()
            
        # Teachers
        teachers = EmployeeProfile.objects.select_related('user', 'role').all()
        teacher_list = []
        for t in teachers:
            record = t.timesheets.filter(date=selected_date).first()
            teacher_list.append({'profile': t, 'record': record})
            
        # Classes & Students
        classes = ClassSchedule.objects.select_related('course', 'teacher').filter(is_active=True).order_by('time_slot')
        class_data = []
        for cs in classes:
            enrollments = cs.enrollments.select_related('student').all()
            student_records = []
            for en in enrollments:
                record = en.daily_records.filter(date=selected_date).first()
                student_records.append({'enrollment': en, 'record': record})
            class_data.append({'class': cs, 'students': student_records})
            
        context['selected_date'] = selected_date
        context['teacher_list'] = teacher_list
        context['class_data'] = class_data
        return context


# ===== CHECKLIST GRID VIEW (ໝາຍຊື່ນັກຮຽນແບບຕາຕະລາງ) =====
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required

@login_required
def checklist_grid_view(request):
    """Grid view for daily student attendance checklist, similar to payroll report."""
    import datetime
    from calendar import monthrange
    from django.db.models import Q
    
    month_query = request.GET.get('month', str(datetime.date.today().month))
    year_query = request.GET.get('year', str(datetime.date.today().year))
    class_id = request.GET.get('class_id', '')
    search_query = request.GET.get('search', '').strip()
    
    try:
        month_int = int(month_query)
        year_int = int(year_query)
        _, num_days = monthrange(year_int, month_int)
    except:
        today = datetime.date.today()
        month_int, year_int = today.month, today.year
        _, num_days = monthrange(year_int, month_int)
    
    # Get all active class schedules for filter dropdown
    all_classes = ClassSchedule.objects.select_related('course', 'teacher').filter(is_active=True).order_by('course__name', 'time_slot')
    
    # Filter enrollments  
    enrollments = Enrollment.objects.select_related(
        'student', 'class_schedule', 'class_schedule__course', 'class_schedule__teacher'
    )
    
    if class_id:
        enrollments = enrollments.filter(class_schedule_id=class_id)
    
    if search_query:
        enrollments = enrollments.filter(
            Q(student__full_name__icontains=search_query) |
            Q(student__nick_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query)
        )
    
    enrollments = enrollments.order_by('class_schedule__course__name', 'student__full_name')
    
    # Pre-fetch all checklist records for the month
    checklist_records = DailyChecklist.objects.filter(
        date__year=year_int, date__month=month_int,
        enrollment__in=enrollments
    )
    
    # Build a lookup dict: {enrollment_id: {day: status}}
    cl_dict = {}
    for rec in checklist_records:
        if rec.enrollment_id not in cl_dict:
            cl_dict[rec.enrollment_id] = {}
        cl_dict[rec.enrollment_id][rec.date.day] = rec.status
    
    lao_weekdays = ['ຈັນ', 'ອັງຄານ', 'ພຸດ', 'ພະຫັດ', 'ສຸກ', 'ເສົາ', 'ອາທິດ']
    days_info = []
    for day in range(1, num_days + 1):
        dt = datetime.date(year_int, month_int, day)
        days_info.append({
            'day': day,
            'weekday': lao_weekdays[dt.weekday()]
        })
        
    days_range = list(range(1, num_days + 1))
    
    # Build rows
    checklist_data = []
    for en in enrollments:
        en_statuses = cl_dict.get(en.id, {})
        daily_statuses = [en_statuses.get(day, '') for day in days_range]
        
        # Count P, L, A, E
        present_count = sum(1 for s in daily_statuses if s == 'P')
        late_count = sum(1 for s in daily_statuses if s == 'L')
        absent_count = sum(1 for s in daily_statuses if s == 'A')
        leave_count = sum(1 for s in daily_statuses if s == 'E')
        
        # Calculate effective hours
        course_type = en.class_schedule.course.class_type
        hours_per_session = 2 if course_type == 'WN' else 1
        effective_hours = (present_count * hours_per_session) + (late_count * hours_per_session * 0.5)
        total_hours = en.class_schedule.total_hours_per_month
        
        # Calculate attendance score (out of 20)
        if total_hours > 0:
            attendance_score = round((effective_hours / float(total_hours)) * 20, 2)
            if attendance_score > 20:
                attendance_score = 20
        else:
            attendance_score = 0
        
        checklist_data.append({
            'enrollment': en,
            'daily_statuses': daily_statuses,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'effective_hours': effective_hours,
            'total_hours': total_hours,
            'attendance_score': attendance_score,
        })
    
    context = {
        'search_query': search_query,
        'month': f"{month_int:02d}",
        'year': str(year_int),
        'month_year': f"{month_int:02d}/{year_int}",
        'days_range': days_range,
        'days_info': days_info,
        'checklist_data': checklist_data,
        'all_classes': all_classes,
        'selected_class_id': class_id,
    }
    return render(request, 'backoffice/templates/checklist_grid.html', context)


@require_POST
def update_checklist(request):
    """AJAX endpoint to update a single DailyChecklist cell."""
    import datetime
    try:
        data = json.loads(request.body)
        enrollment_id = data.get('enrollment_id')
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        status = data.get('status', '').strip()
        
        target_date = datetime.date(year, month, day)
        
        if status in ['P', 'A', 'L', 'E']:
            DailyChecklist.objects.update_or_create(
                enrollment_id=enrollment_id,
                date=target_date,
                defaults={'status': status}
            )
        else:
            # Empty status = delete record
            DailyChecklist.objects.filter(enrollment_id=enrollment_id, date=target_date).delete()
        
        return JsonResponse({'status': 'success', 'message': 'Checklist updated'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def batch_update_checklist(request):
    """AJAX endpoint to batch update daily checklists for one student."""
    import datetime
    try:
        data = json.loads(request.body)
        enrollment_id = data.get('enrollment_id')
        year = int(data.get('year'))
        month = int(data.get('month'))
        updates = data.get('updates', [])
        
        for upd in updates:
            day = int(upd.get('day'))
            status = upd.get('status', '').strip()
            target_date = datetime.date(year, month, day)
            
            if status in ['P', 'A', 'L', 'E']:
                DailyChecklist.objects.update_or_create(
                    enrollment_id=enrollment_id,
                    date=target_date,
                    defaults={'status': status}
                )
            else:
                DailyChecklist.objects.filter(enrollment_id=enrollment_id, date=target_date).delete()
        
        return JsonResponse({'status': 'success', 'message': 'Batch checklist updated'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

