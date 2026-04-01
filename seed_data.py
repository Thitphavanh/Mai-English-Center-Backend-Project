import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from academics.models import Course, ClassSchedule, Student, Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()

# Setup Teachers
teacher_khamvai, _ = User.objects.get_or_create(username='aj_khamvai', defaults={'first_name': 'ອ.ຈ ຄຳໄຫວ ຫຼວງແສນລາດ', 'is_staff': True})
teacher_khamvai.first_name = 'ອ.ຈ ຄຳໄຫວ ຫຼວງແສນລາດ'
teacher_khamvai.save()

teacher_ounphet, _ = User.objects.get_or_create(username='aj_ounphet', defaults={'first_name': 'ອ.ຈ ອຸ່ນເພັດ', 'is_staff': True})

# Setup Courses
course_a_5, _ = Course.objects.get_or_create(name='Class A Frimer', book_name='ເຫຼັ້ມ5', defaults={'description': 'Class A Frimer ເຫຼັ້ມ5'})
course_b_1, _ = Course.objects.get_or_create(name='Class B Frimer', book_name='ເຫຼັ້ມ1', defaults={'description': 'Class B Frimer ເຫຼັ້ມ1'})

# Setup Schedules
schedule_1, _ = ClassSchedule.objects.get_or_create(course=course_a_5, time_slot='06:30 - 07:30 PM', teacher=teacher_khamvai, defaults={'is_active': True})
schedule_2, _ = ClassSchedule.objects.get_or_create(course=course_b_1, time_slot='05:30 - 06:30 PM', teacher=teacher_ounphet, defaults={'is_active': True})
schedule_3, _ = ClassSchedule.objects.get_or_create(course=course_b_1, time_slot='06:30 - 07:30 PM', teacher=teacher_ounphet, defaults={'is_active': True, 'time_slot': '06:30 - 07:30 PM (ຈັນ-ພະຫັດ)'})
if schedule_3.time_slot == '06:30 - 07:30 PM':
    schedule_3.time_slot = '06:30 - 07:30 PM (ຈັນ-ພະຫັດ)'
    schedule_3.save()

def insert_students(data_str, schedule):
    for line in data_str.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 5:
            student_id = parts[1].strip()
            if student_id.isdigit():
                student_id = student_id.zfill(5)
            elif '-' not in student_id and len(student_id) < 5:
                student_id = student_id.zfill(5)
            
            full_name = parts[2].strip()
            nick_name = parts[3].strip()
            phone = parts[4].strip()
            
            student, _ = Student.objects.get_or_create(
                student_id=student_id,
                defaults={'full_name': full_name, 'nick_name': nick_name, 'phone_number': phone}
            )
            student.full_name = full_name
            student.nick_name = nick_name
            student.phone_number = phone
            student.save()
            
            Enrollment.objects.get_or_create(student=student, class_schedule=schedule)

data_1 = """1	00019-MEC	MS ALINA SENGTHAVONG	NANA	 020 22616909
2	00030-MEC	MR PHAMIXAY KHAMPHOUSONE	POTTER	 020 55541272
3	00220-MEC	MS ALIYA	NAMPEUNG	 020 22791456
4	00489	MS MITAPHAP SONEBOULOM	TOUNA	020 97182204
5	00077-MEC	MS PHATSALIDA VILAYSAN	TONFANG	 020 55642330
6	00256-MEC	MS THIDAVANH	JENNY	 020 59626453
7	00020-MEC	MR PHISITSAY SENGTHAVONG	NAI	 020 22616909
8	00009-MEC	MS SOUNISA THAMMAVONG	NAMTHIP	020 55667945
9	00125-MEC	MR PHAMEESOK	WINNER	020 55646945
10	00005-MEC	MR THILATHADA	LEBORN	020 54969494
11	00024-MEC	MR PHOUMIPHON VATANA	ICON	 020 99840886
12	00208-MEC	MR KHAMMEE	KHAM	020 91594304
13	00002-MEC	MS THIPPHAKESONE	PUPE	020 98336999
14	00778	ນາງ ບຸນຮັກສາ ໄກຍະລາດ	ມາຍ	020 94299844
15	00181-MEC	MR PHONEVISIT THAMMAVONG	TON	  020 55440016 
16	00326-MEC	MS CHOULAPHONE	NEIY	 020 77383838"""

data_2 = """1	00646	ນາງ ພອນນະພາ ເທບລືຊາ	ນ້ຳຫອມ	020 58798899
2	00827	ທ້າວ ວັນມີໄຊ ແກ້ວວົງສາ	ອ້າຍ	020 99303040
3	00596	ນາງ ພອນສຸດາ ເພັດໂກສົນ	ໂນເບລ	020 98535050
4	00683	MS Oulaiwan BoudChalernsouk	Nene	020 98566613
5	00684	MS Alisa Vongsengkeo	Minny	020 98566613
6	00823	ທ້າວ ພູມີໄຊ ລັດສະພົນ	ອໍນິວ	020 76389889
7	00766	ນາງ ສຸກທະວີຊັບ ທະວີສຸກ	ໄອລິດ B	020 59228942
8	00824	ນາງ ທິດາສະຫວັນ ດວງມາລາ	ໂຊວ້າ	020 54044497
9	00825	ທ້າວ ສີທະນົນໄຊ ຫຼວງລາດ	ກ໋ອບປີ້	020 96662007
10	00826	ນາງ ຊານິດາ ດາວຮຸ່ງສຸລິ	ຊານິ	020 55665657
11	00828	ນາງ ຊາລິສາ ໄຊຕາ	ເໜືອ	020 92554545
12	00829	ທ້າວ ໄຊພູນຊັບ ພັດທະນາ	ສະແຕ໋ມ	020 93689552
13	00831	ທ້າວ ຈະເລີນຊັບ ເມືອງໂຄດ	ລີໂອ	020 96614956"""

data_3 = """1	00311-MEC	MS LATTANAPHONE	LINA	 020 97664003
2	00316-MEC	MS PHONEVILAY	MELAR	 020 97664003
3	00372	MR SOUKSAWAT	IKKIW	020 28932295
4	00392	MS CHANTHIDA SENALAK	 NALINH	020 96956203
5	00393	 MR KHIWSAVANH SENALAK	 NALONG	020 96956203
6	00064-MEC	MR SOUKMIXAY PHONGMATHEP	OKA	020 22241258
7	00516	MS YANG XU JIN	JENNY	 020 54379964
8	00632	ທ້າວ ການົກພົນ ເທບຄຳຜົງ	ນາຍ	020 95959650
9	00633	ນາງ ອັກສອນສະຫວັນ ສີປະເສີດ	ໂບນັດ	020 22608603
10	00634	ນາງ ປາວີນາ ນັນທະເສນ	ໄອລິດ A	020 98945222
11	00640	MS PANITA KETTAVONG	PIANO	020 94486699
12	00641	ທ້າວ ທະວີຊັບ ອິນທະວົງສາ	ອານິວ	020 77822442
13	00642	ທ້າວ ໄຊສະຫວັດ ຈັນທະລາວັນ	ທັນວາ	020 96644569
14	00768	ນາງ ເພັດທິດາພອນ ຊານລີ	ດ໋ອນລ່າ	020 99111292
15	00726	ທ້າວ ວົງສະກອນ ໄຊສຸລິໂຍ	ບ໋ອນນີ້	020 54614017
16	00643	ທ້າວ ນັນທະກອນ ສຸລິຍະວົງ	ບີມ	020 95742308
17	00807	ນາງ ເພັດໄຟລິນ ສິງທິເດດ	ເອັມມີ້	020 92837029
18	00636	ນາງ ທິບທິດາ ບຸນນະລາດ	ນ້ຳທິບ	020 94181599
19	00815	ທ້າວ ຮຸ່ງທະວີ ດາລາວົງ	ຢູໂລ	020 55199456
20	00816	ທ້າວ ພູສະຫວັນ ຍົກຂັນທອນ	ແຈັກ	020 78971999
21	523	MR PHONEPASERT	JR	020 91119946
22	00804	ທ້າວ ວັນຊະນະ ດາລາວົງ	ໄອເດຍ	020 55199456"""

insert_students(data_1, schedule_1)
insert_students(data_2, schedule_2)
insert_students(data_3, schedule_3)

print("Insertion completed successfully for all 3 classes!")
