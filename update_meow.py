import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from academics.models import *
from datetime import date

student = Student.objects.filter(nick_name__icontains="ແມວ").first()
if student:
    student.full_name = "ນາງ ມຸກຕຸລາ ເທບປັນຍາ"
    student.save()
    
    enrollment = student.enrollments.first()
    if enrollment:
        # Create Assessment
        Assessment.objects.filter(enrollment=enrollment).delete()
        Assessment.objects.create(
            enrollment=enrollment,
            total_score=94.50,
            general_remarks="ນາງ ມຸກຕຸລາ ເປັນຄົນທີ່ຕັ້ງໃຈຮຽນຫຼາຍ, ມີຄວາມກ້າຫານ, ແລະ ທັກສະການຟັງ-ເວົ້າພັດທະນາຂຶ້ນຫຼາຍ. ກະລຸນາສົ່ງເສີມໃຫ້ນ້ອງເບິ່ງກາຕູນພາສາອັງກິດເພີ່ມເຕີມເພື່ອຝຶກສຳນຽງຕື່ມເນີ."
        )
        
        # Create some attendance records
        DailyChecklist.objects.filter(enrollment=enrollment).delete()
        DailyChecklist.objects.create(enrollment=enrollment, date=date(2026, 3, 20), status="P")
        DailyChecklist.objects.create(enrollment=enrollment, date=date(2026, 3, 22), status="P")
        DailyChecklist.objects.create(enrollment=enrollment, date=date(2026, 3, 24), status="L", remark="ມາກາຍ 10 ນາທີ")
        
        # Create tuition fee
        TuitionFee.objects.filter(enrollment=enrollment).delete()
        TuitionFee.objects.create(
            enrollment=enrollment,
            amount=500000.00,
            month="03/2026",
            due_date=date(2026, 3, 5),
            payment_date=date(2026, 3, 1),
            status='P',
            note="ໂອນຜ່ານ BCEL One"
        )
        print("Successfully generated rich records for Meow!")
    else:
        print("No enrollment found for Meow")
else:
    print("Could not find student Meow")
