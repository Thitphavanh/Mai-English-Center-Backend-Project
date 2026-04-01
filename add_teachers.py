import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User
from hr.models import EmployeeProfile, HourlyRateRole

data = """1	ອ.ຈ ຫຼ້າໄກສອນ ໄຊຍະຈິດ	020 22319913
2	ອ.ຈ ດາວໃຈ ຂຽວລືເດດ	020 55224424
3	ອ.ຈ ຄຳໄຫວ ຫຼວງແສນລາດ	020 22603996
4	ອ.ຈ ບົວລຽນ ແກ້ວໂພໄຊ	020 77929276
5	ອ.ຈ ໄຊສະນະ ຊົມຊື່ນ	020 92547246
6	ອ.ຈ ນິດວາລິນ ແສງສະຫວັນ	020 58600038
7	MR. Erik	020 56185474
8	ອ.ຈ ຕຸລີ່	020 96373319
9	ອ.ຈ ແກ່ນຈັນ	020 95120648
10	ອ.ຈ ວົງເພັດ	020 92520986
11	ອ.ຈ ອຸ່ນເພັດ	020 76752028
12	ອ.ຈ ເອ໋	020 98021190
13	ອ.ຈ ໝີນ້ອຍ	020 54224343
14	ອ.ຈ ວັນ	020 78208299
15	ອ.ຈ ແມນ	020 97232549
16	ອາຈານເສີນ	020 98173673"""

print("Starting to add teachers...")
role, _ = HourlyRateRole.objects.get_or_create(name='ຄູສອນທົ່ວໄປ (General Teacher)', defaults={'rate_per_hour': 90000})

lines = data.strip().split('\n')
for i, line in enumerate(lines, 1):
    parts = line.split('\t')
    if len(parts) >= 3:
        name = parts[1].strip()
        phone = parts[2].strip()
        
        # Determine username
        username_str = f"teacher_{i}"
        
        # Some usernames might already be taken from previous seeds (e.g. teacher_1)
        # So check if username is used, and iterate until a free one is found if needed
        # Or just use the exact logic to find if a user with that first_name already exists to avoid dupes
        user = User.objects.filter(first_name=name).first()
        
        if not user:
            # Find a free username
            counter = i
            while User.objects.filter(username=f"teacher_{counter}").exists():
                counter += 1
            username_str = f"teacher_{counter}"
            
            user = User.objects.create_user(
                username=username_str,
                password='MAIteacher123',
                first_name=name,
                is_staff=True
            )
            print(f"Created: {name} (Username: {user.username})")
        else:
            print(f"Skipped, already exists: {name}")
            
        profile, p_created = EmployeeProfile.objects.get_or_create(user=user)
        profile.phone_number = phone
        profile.role = role
        profile.save()

print("All teachers processed successfully!")
