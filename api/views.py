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
    courses = Course.objects.all().order_by('-id')[:6]
    
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
    
    # Course Serializer inside for simplicity or use existing
    course_list = []
    for c in courses:
        course_list.append({
            "id": c.id,
            "name": c.name,
            "book_name": c.book_name,
            "slug": c.slug,
            "description": c.description or "ຫຼັກສູດມາດຕະຖານ ເນັ້ນປູພື້ນຖານ ແລະ ພັດທະນາທັກສະຟັງ ເວົ້າ ອ່ານ ຂຽນ.",
        })

    return Response({
        "success": True,
        "hero": {
            "title": "Master English & EDUCATION AND EXPLORATION",
            "subtitle": "ເສີມສ້າງທັກສະ ຟັງ ເວົ້າ ອ່ານ ຂຽນ ຮຽນມ່ວນ ໃຊ້ງານໄດ້ຈິງ ສອນໂດຍຄູມືອາຊີບ ຈົບຈາກອົດສະຕຣາລີ ພ້ອມປະສົບການສອນກວ່າ 10 ປີ.",
            "stats": stats
        },
        "courses": course_list,
        "features": features
    })
