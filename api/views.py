from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from academics.models import Student
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import StudentSerializer, UserSerializer, TeacherProfileSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def test_message(request):
    image_url = request.build_absolute_uri('/static/images/new-logo.jpg')
    return Response({
        "message": "Hello Mai English Center",
        "image_url": image_url
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def api_portal_login(request):
    student_id = request.data.get('student_id')
    password = request.data.get('password')
    
    user = authenticate(request, username=student_id, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return Response({
            "success": True,
            "message": "ເຂົ້າສູ່ລະບົບສຳເລັດ (Login successful)",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "user": user_data
        })
    else:
        return Response({
            "success": False,
            "error": "Student ID ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ (Invalid ID or Password!)"
        }, status=401)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_portal_dashboard(request):
    if request.user.is_staff:
        return Response({"error": "Staff members should use backoffice."}, status=403)
        
    students = Student.objects.prefetch_related(
        'enrollments__class_schedule__course',
        'enrollments__class_schedule__teacher',
        'enrollments__assessments',
        'enrollments__tuition_fees',
        'enrollments__daily_records'
    ).filter(parent=request.user)
    
    serializer = StudentSerializer(students, many=True, context={'request': request})
    
    return Response({
        "success": True,
        "students": serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_teacher_profile(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id)
    serializer = TeacherProfileSerializer(teacher, context={'request': request})
    return Response({
        "success": True,
        "teacher": serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_home_data(request):
    from academics.models import Course
    from home.models import Announcement, NewsActivity, SchoolHistory, OrgChart
    
    courses = Course.objects.all().order_by('-id')[:6]
    announcements = Announcement.objects.filter(is_active=True).order_by('-date')[:5]
    news = NewsActivity.objects.all().order_by('-date')[:6]
    history = SchoolHistory.objects.first()
    org_chart = OrgChart.objects.first()
    
    # Hero Stats
    stats = [
        {"label": "ປີປະສົບການ", "value": "10+"},
        {"label": "ນັກຮຽນສຳເລັດ", "value": "500+"},
        {"label": "ຄະແນນລີວິວ", "value": "5.0"},
    ]
    
    # Features
    features = [
        {"title": "ຫ້ອງຮຽນໃຫຍ່ ແລະ ສະອາດ", "desc": "ສ້າງບັນຍາກາດການຮຽນໃຫ້ສົດໃສ ແລະ ສະອາດສະອ້ານຕະຫຼອດເວລາ.", "icon": "school"},
        {"title": "ເດີ່ນຫຼິ້ນກາງແຈ້ງກວ້າງຂວາງ", "desc": "ພື້ນທີ່ສຳລັບຜ່ອນຄາຍ ແລະ ເຮັດກິດຈະກຳກາງແຈ້ງສຳລັບນ້ອງໆນັກຮຽນ.", "icon": "child_reaching"},
        {"title": "ອຸປະກອນຄົບຄັນ", "desc": "ມີສື່ການຮຽນການສອນທີ່ທັນສະໄໝ ແລະ ກິດຈະກຳທີ່ຫຼາກຫຼາຍ.", "icon": "science"},
        {"title": "ຫ້ອງຮຽນແອເຢັນທຸກຫ້ອງ", "desc": "ຫ້ອງຮຽນຕິດແອ A > B > C > D ໃຫ້ຜູ້ຮຽນມີຄວາມສະດວກສະບາຍ.", "icon": "ac_unit"},
    ]
    
    course_list = []
    for c in courses:
        course_list.append({
            "id": c.id,
            "name": c.name,
            "book_name": c.book_name,
            "slug": c.slug,
            "description": c.description or "ຫຼັກສູດມາດຕະຖານ ເນັ້ນປູພື້ນຖານ ແລະ ພັດທະນາທັກສະຟັງ ເວົ້າ ອ່ານ ຂຽນ.",
            "image_url": request.build_absolute_uri(c.thumbnail.url) if c.thumbnail else None,
        })

    announcement_list = []
    for a in announcements:
        announcement_list.append({
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "date": a.date.strftime("%d %b %Y")
        })

    news_list = []
    for n in news:
        news_list.append({
            "id": n.id,
            "title": n.title,
            "description": n.description,
            "image": request.build_absolute_uri(n.image.url) if n.image else None,
            "date": n.date.strftime("%d %b %Y")
        })

    return Response({
        "success": True,
        "hero": {
            "title": "Master English & EDUCATION AND EXPLORATION",
            "subtitle": "ເສີມສ້າງທັກສະ ຟັງ ເວົ້າ ອ່ານ ຂຽນ ຮຽນມ່ວນ ໃຊ້ງານໄດ້ຈິງ ສອນໂດຍຄູມືອາຊີບ ຈົບຈາກອົດສະຕຣາລີ ພ້ອມປະສົບການສອນກວ່າ 10 ປີ.",
            "stats": stats
        },
        "courses": course_list,
        "features": features,
        "announcements": announcement_list,
        "news": news_list,
        "history": {
            "title": history.title if history else "ປະຫວັດຂອງໂຮງຮຽນ",
            "content": history.content if history else "...",
            "image": request.build_absolute_uri(history.image.url) if history and history.image else None
        },
        "org_chart": request.build_absolute_uri(org_chart.image.url) if org_chart and org_chart.image else None
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_course_detail(request, slug):
    from academics.models import Course
    course = get_object_or_404(Course, slug=slug)
    
    return Response({
        "success": True,
        "course": {
            "id": course.id,
            "name": course.name,
            "book_name": course.book_name,
            "slug": course.slug,
            "description": course.description or "ຫຼັກສູດມາດຕະຖານ ເນັ້ນປູພື້ນຖານການນຳໃຊ້ພາສາອັງກິດຢ່າງຖືກຕ້ອງ ແລະ ໝັ້ນໃຈ.",
            "image_url": request.build_absolute_uri(course.thumbnail.url) if course.thumbnail else None,
            "class_type_display": course.get_class_type_display(),
            "teaching_days": course.teaching_days,
            "created_at": course.created_at.strftime("%d %b %Y"),
            "benefits": [
                "ພັດທະນາທັກສະການອອກສຽງ (Pronunciation) ໃຫ້ຖືກຕ້ອງ.",
                "ຮຽນຮູ້ຄຳສັບ ແລະ ໄວຍາກອນທີ່ຈຳເປັນໃນຊີວິດປະຈຳວັນ.",
                "ສ້າງຄວາມໝັ້ນໃຈໃນການສື່ສານກັບຊາວຕ່າງຊາດ.",
                "ສິ່ງອຳນວຍຄວາມສະດວກໃນການຮຽນທີ່ທັນສະໄໝ."
            ],
            "contact": {
                "whatsapp": "+856 20 98 651 110",
                "location": "ບ້ານໄຊຍະມຸງຄຸນ ນະຄອນໄກສອນ ແຂວງສະຫວັນນະເຂດ"
            }
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_course_list(request):
    from academics.models import Course
    from django.core.paginator import Paginator
    
    courses_qs = Course.objects.all().order_by('-id')
    paginator = Paginator(courses_qs, 10) # 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    course_list = []
    for c in page_obj:
        course_list.append({
            "id": c.id,
            "name": c.name,
            "book_name": c.book_name,
            "slug": c.slug,
            "description": c.description or "ຫຼັກສູດມາດຕະຖານ ເນັ້ນປູພື້ນຖານການນຳໃຊ້ພາສາອັງກິດຢ່າງຖືກຕ້ອງ ແລະ ໝັ້ນໃຈ.",
            "image_url": request.build_absolute_uri(c.thumbnail.url) if c.thumbnail else None,
        })
        
    return Response({
        "success": True,
        "courses": course_list,
        "has_next": page_obj.has_next(),
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_popups(request):
    from communication.models import PopupMessage
    from django.db.models import Q, Count
    
    # Get messages that are active AND (either for all users OR specifically for this user)
    # We use Count to identify messages with 0 target users (send to all)
    popups = PopupMessage.objects.filter(
        is_active=True
    ).annotate(
        num_targets=Count('target_users')
    ).filter(
        Q(num_targets=0) | Q(target_users=request.user)
    ).distinct().order_by('-created_at')
    
    popup_list = []
    for p in popups:
        popup_list.append({
            "id": p.id,
            "title": p.title,
            "message": p.message,
            "image": request.build_absolute_uri(p.image.url) if p.image else None,
        })
        
    return Response({
        "success": True,
        "popups": popup_list
    })
