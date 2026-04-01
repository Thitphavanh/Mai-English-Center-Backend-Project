import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()

from django.contrib.auth.models import User
from hr.models import EmployeeProfile, HourlyRateRole, Timesheet

raw_data = """
1	ອ.ຈ ຫຼ້າໄກສອນ ໄຊຍະຈິດ	020 22319913																															0	  -   	
2	ອ.ຈ ດາວໃຈ ຂຽວລືເດດ	020 55224424	2	2	2	2		2		2	2							2	3	3	1	3		2	1	3	3	3	3		2	2	45	  4,050,000 	
3	ອ.ຈ ຄຳໄຫວ ຫຼວງແສນລາດ	020 22603996			2							2		2	2				2		2	2				2	2	2	2		2		24	  1,920,000 	
4	ອ.ຈ ບົວລຽນ ແກ້ວໂພໄຊ	020 77929276				2	2	2												2	2	2		2	2	2	2	2			2	2	26	  2,080,000 	
5	ອ.ຈ ໄຊສະນະ ຊົມຊື່ນ	020 92547246			2		2	2				2	2	3					2	2	2	2				2	1	1					25	  2,000,000 	
6	ອ.ຈ ນິດວາລິນ ແສງສະຫວັນ	020 58600038	2	2	2			2			2	2		2	2		2	2							2				1			2	25	  2,000,000 	
7	MR. Erik	020 56185474			2	2	2	1				2	2	2	1				2	2	2	1											21		
8	ອ.ຈ ຕຸລີ່	020 96373319	2							2	2						2								2						2	2	14	  1,120,000 	
9	ອ.ຈ ແກ່ນຈັນ	020 95120648	2	2						2	2						2	2						2	1								15		
10	ອ.ຈ ວົງເພັດ	020 92520986										3	3		3																		9	  720,000 	
11	ອ.ຈ ອຸ່ນເພັດ	020 76752028	2	2						2							2	2						2	2						2	2	18	  1,440,000 	
12	ອ.ຈ ເອ໋	020 98021190		2						2	2						2	2											2				12	  960,000 	
13	ອ.ຈ ໝີນ້ອຍ	020 54224343			3	3	3	2																									11	  880,000 	
14	ອ.ຈ ວັນ	020 78208299											2	2	1				2	2	2	1				2	2	2	2				20	  1,600,000 	
15	ອ.ຈ ແມນ	020 97232549																						2									2	  160,000 	
16	ອາຈານເສີນ	020 98173673			1	1	1	1				1	1	1	1				1	1	1	1				1	1	1	1				16	  2,400,000 	
"""

role_90k, _ = HourlyRateRole.objects.get_or_create(name='General Teacher (90,000LAK)', defaults={'rate_per_hour': 90000})
role_80k, _ = HourlyRateRole.objects.get_or_create(name='General Teacher (80,000LAK)', defaults={'rate_per_hour': 80000})
role_150k, _ = HourlyRateRole.objects.get_or_create(name='Special Teacher (150,000LAK)', defaults={'rate_per_hour': 150000})

lines = raw_data.strip().split('\n')
for line in lines:
    parts = line.split('\t')
    # Pad missing empty cells at the end of the line if necessary
    if len(parts) < 36:
        parts += [''] * (36 - len(parts))
        
    seq = parts[0].strip()
    name = parts[1].strip()
    phone = parts[2].strip()

    assigned_role = role_80k
    if "ດາວໃຈ" in name:
        assigned_role = role_90k
    elif "ເສີນ" in name:
        assigned_role = role_150k

    username = f"teacher_{seq}"
    user, created = User.objects.get_or_create(username=username, defaults={
        'first_name': name,
        'email': f"{username}@mai.com"
    })
    if not created:
         user.first_name = name
         user.save()

    profile, _ = EmployeeProfile.objects.get_or_create(user=user, defaults={
        'phone_number': phone,
        'role': assigned_role
    })
    
    if profile.phone_number != phone or profile.role != assigned_role:
        profile.phone_number = phone
        profile.role = assigned_role
        profile.save()

    # Days 1 to 30 mapped to parts[3]...parts[32]
    for day_idx in range(30):
        col_idx = 3 + day_idx
        if col_idx < len(parts):
            val_str = parts[col_idx].strip()
            if val_str and val_str.replace('.', '', 1).isdigit():
                hours = float(val_str)
                if hours > 0:
                    d = date(2025, 11, day_idx + 1)
                    Timesheet.objects.update_or_create(
                        employee=profile,
                        date=d,
                        defaults={'hours_worked': hours}
                    )

print("Data seeded successfully!")
