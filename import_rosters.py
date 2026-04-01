import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from academics.models import Student, Course, ClassSchedule, Enrollment
from django.utils import timezone
import random

data1 = """1	ແມວ	NANA	QUOC	ນ້ຳຫອມ	LINA	 KHAIMUK	LIENMAY	Ball
2	DA DA	POTTER	NALINH	ອ້າຍ	MELAR	BANA	IG	Tono 
3	BOTAN	NAMPEUNG	MINY	ໂນເບລ	IKKIW	HOT	TONKA	Nong 
4	MOUNIN	TOUNA	MEE 	Nene	 NALINH	MESSI	CU TUAN	King
5	ເບຍ	TONFANG	Tono	Minny	 NALONG	HONEY	ບິວ	Kitty
6	ບີບີ	JENNY	GAME	ອໍນິວ	OKA	ບິກບອຍ	ຊອນ	Mouyong
7	ແມນຢູ	NAI		ໄອລິດ B	JENNY	ຊັນ	NEIY 	LookPa
8	ແອັມພາ	POPPY		ໂຊວ້າ	ນາຍ	ເໝີຍລີ້	ອິນນາ	Ploysai
9	ປີໃຫມ່	NAMTHIP		ກ໋ອບປີ້	ໂບນັດ	DEW	ຄິດຕຣີນ	Phou
10	ມາລິກ້າ	WINNER		ຊານິ	ໄອລິດ A	ນາງ	 IDIW	BELLA
11	ໂດນັດ	LEBORN		ເໜືອ	PIANO	ເມລີ້	VIEWNA	ELLY
12	ວາໂຢ	ICON		ສະແຕ໋ມ	ອານິວ	ຕິ໋ງນ໋ອຍ	ນາຍ	Nounim
13	ໄທກ້າ	KHAM		ລີໂອ	ທັນວາ	YAYA	ແບ້ງ	Meiy
14	TENGMO	PUPE			ດ໋ອນລ່າ	TANOY	ຄິວ	Nampou
15	ເນີຍ	ມາຍ			ບ໋ອນນີ້	TOUKTA	Bobby	Angie
16	ເຂົ້າໃຫມ່	TON			ບີມ	A LIN	ມຸກ	 Anda
17	ນິວ	NEIY			ເອັມມີ້	NEW	ນ້ຳຟ້າ	ກຸຕຸ່ງ
18	ຣຸ້ງ				ນ້ຳທິບ	KHAIMOUK	ນຸດນີ້	THING THING
19	ຊັນນີ້				ຢູໂລ	ສົ້ມໂອ	ບ໋ອນ	Bella
20	ອາເລັກ				ແຈັກ	ເໝີຍ	ແອັມດາ	ອາຕີ້
21	ເໝືອນຝັນ				ປູຕິນ	Donat	TITAN	WINNER
22	ເອັມມີ້				JR	ມິມີ່	NINE	ໂກແບັກ
23							ມິນ	FA
24								CHAMMY
25								Neuang"""

cols1 = [
    ("Class A", "5:30-6:30"),
    ("Class A", "6:30-7:30"),
    ("Class B", "6:30-7:30"),
    ("Class B", "5:30-6:30"),
    ("Class C", "6:30-7:30"),
    ("Class C", "5:30-6:30"),
    ("Class D", "6:30-7:30"),
    ("Class D", "5:30-6:30"),
]

data2 = """1	ໂກເບລ	ມ້ອນ	EM LAN	JONO	MINY	ຕຸລາ
2	ແອນນາ	NO AN	ມັງກອນ	SUNDAY	YUME	ຄິມມີ້
3	ອາລິດ	ຫາວ	ARUN	NAT	EM HEUANG	ໂບວີ້
4	ອາເທີ້	ອາເກມ	SAM	KIMMY	KHAIMUK 	ແອັ໋ນຈີ້
5	ຢູໂລ	ເອັກຕ້າ	NAMKHING	KHAOMAI	KOUGNANG	ໂຕໂນ້
6	ນ້ຳຝົນ	ຈູເນ່ຍ	ນ້ຳຟ້າ	KA	BEAR	ຈີຢອນ
7	ຫົງຟ້າ	WENDY	DEW	BEEM	KHUN	ບອນ
8	ມິໂນ່	ກັບຕັນ	ບອຍ	BORM	TAK	ລີ້
9	ບີເອັມ	ອໍໂຕ້	ເດຍ	BOY	Xaiy	ໃບເພີນ
10	ໄຂ່ມຸກ	ອັສຕິນ	ກິມຫງັອກ	ເພັນນີ້	TOIY	ແອັມເຮືອງ
11	ອໍໂຕ້	ຄຣີດ	ໄຂ່ມຸກ	ປາວານ	LIENXAY	ສົ້ມໂອ
12	ອໍລ້າ	ມິນຕັ້ນ	ບິວ	ອາລິດ	ລີນຊານ	ບອສ
13	ນີນ້າ	ນະເດດ	ອຸບົນ	ຊັບປີ້	ແກຣມ	ແບັ້ງ
14	ບ໋ອນ	NAMNIN	 LIANKHAM	ເຊບ	San	ບີບີ່
15	ຊົມພຸ້	ເຂົ້າພູນ	ອັນຊັນ	ອັງເປົາ	TITON	
16	ແອນນີ້	ອໍກ້າ	ຕົ້ນກ້າ	ປັນ ປັນ	BAND	
17	ໝູທອງ	ແຈມມິນ		BAO	ໂນ້	
18	ແອັມມ່າ	ດີໂດ້		NOM	MAKEE	
19	ຄີລຽນ	ນິນນີ້		 ເຈັ໋ງໆ	TINA	
20	ແຮັບປີ້	ເຕຊິນ			HENG HENG	
21	ຣັກກີ້	ອາລັນ				
22	ເກັ່ງ					
23						
24						
25						"""

cols2 = [
    ("ເສົາ-ທິດ A", "10.00-12.00"),
    ("ເສົາ-ທິດ B", "10.00-12.00"),
    ("ເສົາ-ທິດ C", "10.00-12.00"),
    ("ເສົາ-ທິດ D", "10.00-12.00"),
    ("ເສົາ-ທິດ E", "10.00-12.00"),
    ("E ພາສາຈີນ", "06.00-07.00"),
]

def generate_student_id():
    while True:
        sid = f"{random.randint(1000, 99999):05d}"
        if not Student.objects.filter(student_id=sid).exists():
            return sid

print("Creating classes and importing students...")

def process_block(data_str, cols):
    # Create courses
    schedules = []
    for cname, tslot in cols:
        course, _ = Course.objects.get_or_create(name=cname)
        cs, _ = ClassSchedule.objects.get_or_create(
            course=course, time_slot=tslot, 
            defaults={'start_date': timezone.now().date(), 'end_date': timezone.now().date()}
        )
        schedules.append(cs)
        
    lines = data_str.strip().split('\n')
    for line in lines:
        parts = line.split('\t')
        if len(parts) > 1:
            # part 0 is row number
            for col_idx in range(1, len(parts)):
                name = parts[col_idx].strip()
                if name:
                    # check col bounds
                    if col_idx - 1 < len(schedules):
                        cs = schedules[col_idx - 1]
                        
                        # Create student
                        sid = generate_student_id()
                        student, created = Student.objects.get_or_create(
                            full_name=name,
                            defaults={
                                'nick_name': name,
                                'student_id': sid
                            }
                        )
                        
                        # Create Enrollment
                        Enrollment.objects.get_or_create(
                            student=student,
                            class_schedule=cs,
                            defaults={'enrollment_date': timezone.now().date()}
                        )

process_block(data1, cols1)
process_block(data2, cols2)

print("Finished importing!")
