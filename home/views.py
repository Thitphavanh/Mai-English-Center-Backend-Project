from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from academics.models import Student
from django.db.models import Q

@api_view(['GET'])
@permission_classes([AllowAny])
def test_message(request):
    image_url = request.build_absolute_uri('/static/images/new-logo.jpg')
    return Response({
        "message": "Hello Mai English Center",
        "image_url": image_url
    })

def index(request):
    return render(request, 'index.html')

def check_enrollment(request):
    query = request.GET.get('q', '')
    results = None
    if query:
        # Search student by exact or partial name/nickname
        # We don't require login for this, so we only display safe info (Name, Nickname, Class)
        results = Student.objects.prefetch_related('enrollments__class_schedule__course').filter(
            Q(full_name__icontains=query) | 
            Q(nick_name__icontains=query) |
            Q(student_id__iexact=query)
        ).distinct()
        
    return render(request, 'home/check_enrollment.html', {
        'query': query,
        'results': results
    })

def student_detail(request, student_id):
    from django.shortcuts import get_object_or_404
    student = get_object_or_404(Student.objects.prefetch_related(
        'enrollments__class_schedule__course',
        'enrollments__class_schedule__teacher',
        'enrollments__assessments',
        'enrollments__tuition_fees',
        'enrollments__daily_records'
    ), student_id__iexact=student_id)
    
    return render(request, 'home/student_detail.html', {'student': student})

def teacher_profile(request, teacher_id):
    from django.shortcuts import get_object_or_404
    from django.contrib.auth import get_user_model
    User = get_user_model()
    teacher = get_object_or_404(User, id=teacher_id)
    # Get all class schedules for this teacher
    class_schedules = teacher.teaching_classes.all() if hasattr(teacher, 'teaching_classes') else []
    
    return render(request, 'home/teacher_profile.html', {
        'teacher': teacher,
        'class_schedules': class_schedules,
    })

def class_rosters(request):
    from academics.models import ClassSchedule
    schedules = list(ClassSchedule.objects.prefetch_related('course', 'enrollments__student').all())
    
    reg_configs = [
        {"name": "Class A", "time": "5:30-6:30", "anchor": "ແມວ"},
        {"name": "Class A", "time": "6.30-7.30", "anchor": "NANA"},
        {"name": "Class A", "time": "6.30-7.30", "anchor": "QUOC"},
        {"name": "Class B", "time": "5:30-6:30", "anchor": "ນ້ຳຫອມ"},
        {"name": "Class B", "time": "6.30-7.30", "anchor": "LINA"},
        {"name": "Class C", "time": "5:30-6:30", "anchor": "KHAIMUK"},
        {"name": "Class C", "time": "6.30-7.30", "anchor": "LIENMAY"},
        {"name": "Class D", "time": "5:30-6:30", "anchor": "Ball"},
    ]
    
    wk_configs = [
        {"name": "ເສົາ-ທິດ A", "time": "10.00-12.00", "anchor": "ໂກເບລ"},
        {"name": "ເສົາ-ທິດ B", "time": "10.00-12.00", "anchor": "ມ້ອນ"},
        {"name": "ເສົາ-ທິດ C", "time": "10.00-12.00", "anchor": "EM LAN"},
        {"name": "ເສົາ-ທິດ D", "time": "10.00-12.00", "anchor": "JONO"},
        {"name": "ເສົາ-ທິດ E", "time": "10.00-12.00", "anchor": "MINY"},
        {"name": "E ພາສາຈີນ", "time": "06.00-07.00", "anchor": "ຕຸລາ"},
    ]
    
    # Students with Scholarship to mark green
    green_students = ["QUOC", "NALINH", "MINY", "MEE", "ນ້ຳທິບ", "ມາຍ", "KIMMY", "HENG HENG", "ບອສ", "POPPY"]
    
    class MockSchedule:
        def __init__(self, name, time_slot, real_cs=None):
            self.display_name = name
            self.display_time = time_slot
            self.real_cs = real_cs
            
            if real_cs:
                self.count = real_cs.enrollments.count()
                self.all_students = list(real_cs.enrollments.all())
            else:
                self.count = 0
                self.all_students = []

    def match_schedule(anchor, schedules_list):
        for cs in schedules_list:
            for enr in cs.enrollments.all():
                if enr.student.nick_name and anchor.upper() in enr.student.nick_name.upper():
                    return cs
                if enr.student.full_name and anchor.upper() in enr.student.full_name.upper():
                    return cs
        return None

    reg_schedules = []
    for c in reg_configs:
        cs = match_schedule(c['anchor'], schedules)
        reg_schedules.append(MockSchedule(c['name'], c['time'], cs))
        
    wk_schedules = []
    for c in wk_configs:
        cs = match_schedule(c['anchor'], schedules)
        wk_schedules.append(MockSchedule(c['name'], c['time'], cs))
        
    def build_pivot(schedule_list):
        if not schedule_list: return [], []
        max_count = max([mock.count for mock in schedule_list] + [25])
        rows = []
        
        for i in range(max_count):
            row = []
            for mock in schedule_list:
                if i < mock.count:
                    student = mock.all_students[i].student
                    name = student.nick_name or student.full_name
                    is_green = name in green_students
                    row.append({
                        'name': name, 
                        'green': is_green,
                        'student_id': student.student_id or '',
                        'full_name': student.full_name or ''
                    })
                else:
                    row.append({'name': '', 'green': False, 'student_id': '', 'full_name': ''})
            if i < 25 or any(r['name'] for r in row):
                rows.append(row)
            
        totals = [mock.count for mock in schedule_list]
        return rows, totals

        
    reg_rows, reg_totals = build_pivot(reg_schedules)
    wk_rows, wk_totals = build_pivot(wk_schedules)

    return render(request, 'home/class_rosters.html', {
        'reg_schedules': reg_schedules, 'reg_rows': reg_rows, 'reg_totals': reg_totals, 'reg_sum': sum(reg_totals),
        'wk_schedules': wk_schedules, 'wk_rows': wk_rows, 'wk_totals': wk_totals, 'wk_sum': sum(wk_totals),
    })

def portal_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('home:portal_dashboard')
        
    error = None
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        
        user = authenticate(request, username=student_id, password=password)
        if user is not None:
            login(request, user)
            return redirect('home:portal_dashboard')
        else:
            error = "Student ID ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ (Invalid ID or Password!)"
            
    return render(request, 'home/portal_login.html', {'error': error})

from django.contrib.auth.models import User

def portal_register(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('home:portal_dashboard')
        
    error = None
    success = False
    
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        parent_name = request.POST.get('parent_name')
        
        # 1. Check if student exists
        student = Student.objects.filter(student_id=student_id).first()
        
        if not student:
            error = "ບໍ່ພົບຂໍ້ມູນນັກຮຽນລະຫັດນີ້! (Student ID not found)"
        elif student.parent is not None:
            error = "ລະຫັດນັກຮຽນນີ້ມີຜູ້ປົກຄອງລົງທະບຽນແລ້ວ! (Already registered)"
        elif not phone or phone.strip().replace(' ', '') not in str(student.phone_number).replace(' ', ''):
            # Extra security: Phone number must partially match what's in the DB
            error = "ເບີໂທລະສັບບໍ່ກົງກັບທີ່ມອບໃຫ້ໂຮງຮຽນກ່ອນໜ້ານີ້! (Phone number mismatch)"
        else:
            # 2. Check if username (student_id) exists in User table just in case
            if User.objects.filter(username=student_id).exists():
                error = "ບັນຊີນີ້ເຄີຍຖືກສ້າງໄປແລ້ວ ແຕ່ຍັງບໍ່ທັນເຊື່ອມໂຍງ! ລົບກວນແຈ້ງແອັດມິນ."
            else:
                # 3. Create User & Link
                user = User.objects.create_user(
                    username=student_id,
                    password=password,
                    first_name=parent_name,
                    is_staff=False
                )
                student.parent = user
                student.save()
                
                # Auto login
                login(request, user)
                return redirect('home:portal_dashboard')
                
    return render(request, 'home/portal_register.html', {'error': error, 'success': success})

def portal_logout(request):
    logout(request)
    return redirect('home:portal_login')

@login_required(login_url='/en/portal/login/')
def portal_dashboard(request):
    # Route Staff back to backoffice if they wander here
    if request.user.is_staff:
        return redirect('backoffice:dashboard')
        
    # Get all students linked to this parent
    students = Student.objects.prefetch_related(
        'enrollments__class_schedule__course',
        'enrollments__class_schedule__teacher',
        'enrollments__assessments',
        'enrollments__tuition_fees',
        'enrollments__daily_records'
    ).filter(parent=request.user)
    
    context = {
        'students': students,
    }
    return render(request, 'home/portal_dashboard.html', context)

from academics.models import ClassSchedule, Enrollment, Assessment, AssessmentCriteria, AssessmentDetail
from django.contrib.auth import get_user_model
import json

# View ສຳລັບໜ້າປະເມີນຜົນ
def learning_assessment(request):
    User = get_user_model()
    success = False
    error_msg = None

    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment_id")
        professor_id  = request.POST.get("professor_id")

        score_activity   = request.POST.get("score_activity")   or None
        score_attendance = request.POST.get("score_attendance") or None
        score_quiz       = request.POST.get("score_quiz")       or None
        score_exercise   = request.POST.get("score_exercise")   or None
        gpa              = request.POST.get("gpa")              or None

        listening = request.POST.get("listening_skill", "")
        speaking  = request.POST.get("speaking_skill", "")
        reading   = request.POST.get("reading_skill", "")
        writing   = request.POST.get("writing_skill", "")

        try:
            assessment = Assessment.objects.create(
                enrollment_id    = enrollment_id,
                evaluator_id     = professor_id,
                score_activity   = score_activity,
                score_attendance = score_attendance,
                score_quiz       = score_quiz,
                score_exercise   = score_exercise,
                gpa              = gpa,
                listening_remark = listening,
                speaking_remark  = speaking,
                reading_remark   = reading,
                writing_remark   = writing,
            )

            criteria_names = [
                "Lesson Understanding",
                "Communication Skills",
                "Responsibility (Assignments)",
                "Activities Participation",
                "Group Collaboration"
            ]
            for i, name in enumerate(criteria_names, start=1):
                rating = request.POST.get(f"perf_{i}")
                if rating:
                    crit, _ = AssessmentCriteria.objects.get_or_create(
                        name_en=name, defaults={'order': i}
                    )
                    AssessmentDetail.objects.create(
                        assessment=assessment, criteria=crit, rating=rating
                    )

            success = True
        except Exception as e:
            error_msg = str(e)


    teachers = User.objects.filter(is_staff=True)
    classes = ClassSchedule.objects.select_related('course').all()
    # Prefetch monthly_scores to get the latest one for auto-pull
    enrollments = Enrollment.objects.select_related('student', 'class_schedule').prefetch_related('monthly_scores').all()

    classes_data = [
        {
            'id': c.id,
            'label': f"{c.course.name} — {c.time_slot}",
            'teacher_id': c.teacher_id,
        } for c in classes
    ]

    enrollments_data = []
    for e in enrollments:
        # Try to find the most recent monthly score
        latest_score_obj = e.monthly_scores.order_by('-id').first() # ID order as a proxy for recency if month sorting is tricky
        score_data = None
        if latest_score_obj:
            score_data = {
                'activity': float(latest_score_obj.engagement) if latest_score_obj.engagement is not None else 0,
                'attendance': float(latest_score_obj.attendance) if latest_score_obj.attendance is not None else 0,
                'quiz': float(latest_score_obj.monthly_test) if latest_score_obj.monthly_test is not None else 0,
                'exercise': float(latest_score_obj.exercise) if latest_score_obj.exercise is not None else 0,
            }

        enrollments_data.append({
            'id': e.id,
            'student_name': e.student.full_name or e.student.nick_name or str(e.student),
            'student_nick': e.student.nick_name or '',
            'student_id_code': e.student.student_id or "",
            'class_id': e.class_schedule_id,
            'latest_score': score_data,
        })

    context = {
        'teachers': teachers,
        'classes_json': json.dumps(classes_data),
        'enrollments_json': json.dumps(enrollments_data),
        'success': success,
        'error_msg': error_msg,
    }

    return render(request, 'home/learning_assessment_form.html', context)
