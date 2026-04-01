from django.db import models
from django.contrib.auth import get_user_model

# Get custom user model if defined
User = get_user_model()



class Course(models.Model):
    """ Model to store Course / Book information (e.g., FRIMER BOOK 1) """
    name = models.CharField(max_length=150, help_text="Course Name e.g., CLASS A FRIMER")
    book_name = models.CharField(max_length=150, help_text="e.g., BOOK 1", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Course (ຫຼັກສູດ/ປຶ້ມ)"
        verbose_name_plural = "Courses (ລາຍການຫຼັກສູດ)"

    def __str__(self):
        return f"{self.name} - {self.book_name}"

class ClassSchedule(models.Model):
    """ Model to represent a specific class schedule (e.g., TIME 05:30 - 06:30 PM) """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_classes')
    time_slot = models.CharField(max_length=100, help_text="e.g., 05:30 - 06:30 PM")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Class Schedule (ຕາຕະລາງຮຽນ)"
        verbose_name_plural = "Class Schedules (ຕາຕະລາງຮຽນທັງໝົດ)"

    def __str__(self):
        return f"{self.course.name} ({self.time_slot})"

class Student(models.Model):
    """ Model to represent Student profiles from the Excel checklist """
    student_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID STUDENT (e.g., 00601)")
    full_name = models.CharField(max_length=255, help_text="NAME AND FAMILY NAME (e.g., ນາງ ມຸກຕຸລາ ເທບປັນຍາ)")
    nick_name = models.CharField(max_length=100, blank=True, null=True, help_text="NICK NAME (e.g., ແມວ)")
    phone_number = models.CharField(max_length=50, blank=True, null=True, help_text="Phone number (e.g., 020 96769512)")
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student (ນັກຮຽນ)"
        verbose_name_plural = "Students (ລາຍຊື່ນັກຮຽນ)"

    def save(self, *args, **kwargs):
        if not self.student_id or str(self.student_id).strip() == '':
            # ຫາ ID ຫຼ້າສຸດທີ່ເປັນຕົວເລກລ້ວນ
            last_student = Student.objects.filter(student_id__regex=r'^\d+$').order_by('-student_id').first()
            if last_student and last_student.student_id:
                next_id = int(last_student.student_id) + 1
                self.student_id = f"{next_id:05d}"
            else:
                self.student_id = "00001"
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name

class Enrollment(models.Model):
    """ Links Students to a specific ClassSchedule """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Enrollment (ການລົງທະບຽນຮຽນ)"
        verbose_name_plural = "Enrollments (ການລົງທະບຽນຮຽນ)"
        unique_together = ['student', 'class_schedule']

    def __str__(self):
        return f"{self.student.full_name} -> {self.class_schedule}"

class DailyChecklist(models.Model):
    """ 
    Model to track the 1-31 days columns from the Excel sheet. 
    Usually tracks Attendance or Daily Scores.
    """
    class StatusChoices(models.TextChoices):
        PRESENT = 'P', 'Present (ມາ)'
        ABSENT = 'A', 'Absent (ຂາດ)'
        LATE = 'L', 'Late (ມາສາຍ)'
        LEAVE = 'E', 'Leave (ລາ)'

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='daily_records')
    date = models.DateField(help_text="The specific day (1-31) of the month the record is for")
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.PRESENT)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="If checklist implies score grading")
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Daily Checklist (ປຶ້ມຕິດຕາມປະຈຳວັນ)"
        verbose_name_plural = "Daily Checklists (ປຶ້ມຕິດຕາມປະຈຳວັນ)"
        unique_together = ['enrollment', 'date']
        ordering = ['date']

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.date} - {self.get_status_display()}"


class Assessment(models.Model):
    """ Overall Learning Assessment and Evaluation record for a student in a class """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='assessments')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evaluations_given', help_text="Professor/Teacher")
    evaluation_date = models.DateField(auto_now_add=True)
    
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    general_remarks = models.TextField(blank=True, null=True)
    listening_remark = models.TextField(blank=True, null=True, verbose_name="Listening Skill")
    speaking_remark = models.TextField(blank=True, null=True, verbose_name="Speaking Skill")
    reading_remark = models.TextField(blank=True, null=True, verbose_name="Reading Skill")
    writing_remark = models.TextField(blank=True, null=True, verbose_name="Writing Skill")

    class Meta:
        verbose_name = "Assessment (ການປະເມີນຜົນ)"
        verbose_name_plural = "Assessments (ແບບປະເມີນຜົນການຮຽນ)"

    def __str__(self):
        return f"Assessment for {self.enrollment.student.full_name} on {self.evaluation_date}"


class AssessmentCriteria(models.Model):
    """ Master list of criteria to evaluate (e.g., Lesson Understanding, Communication Skills) """
    name_en = models.CharField(max_length=255, help_text="e.g., Lesson Understanding")
    name_lo = models.CharField(max_length=255, help_text="e.g., ຄວາມເຂົ້າໃຈໃນການຮຽນ", blank=True, null=True)
    category = models.CharField(max_length=255, help_text="e.g., ປະເມີນພຶດຕິກຳ I", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Assessment Criteria (ຫົວຂໍ້ປະເມີນ)"
        verbose_name_plural = "Assessment Criterias (ຫົວຂໍ້ປະເມີນ)"
        ordering = ['order']

    def __str__(self):
        return f"{self.name_en} ({self.name_lo})"


class AssessmentDetail(models.Model):
    """ Individual score line items tied to an Assessment """
    class RatingChoices(models.IntegerChoices):
        OUTSTANDING = 5, 'Outstanding (ດີເດັ່ນ)'
        EXCELLENT = 4, 'Excellent (ດີຫລາຍ)'
        VERY_GOOD = 3, 'Very Good (ດີ)'
        AVERAGE = 2, 'Average (ປານກາງ)'
        BELOW_AVERAGE = 1, 'Below Average (ຕ່ຳກວ່າເກນ)'

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='details')
    criteria = models.ForeignKey(AssessmentCriteria, on_delete=models.PROTECT, related_name='evaluated_details')
    rating = models.IntegerField(choices=RatingChoices.choices, help_text="Score from 1 to 5")
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Assessment Detail (ລາຍລະອຽດປະເມີນ)"
        verbose_name_plural = "Assessment Details (ລາຍລະອຽດປະເມີນ)"
        unique_together = ['assessment', 'criteria']

    def __str__(self):
        return f"{self.assessment} - {self.criteria.name_en}: {self.get_rating_display()}"




class TuitionFee(models.Model):
    """ ຮອງຮັບຂໍ້ມູນຈາກໄຟລ໌ `ຄ່າຮຽນ ເດືອນ04-2026.xlsx` """
    class FeeStatus(models.TextChoices):
        PAID = 'P', 'Paid (ຈ່າຍແລ້ວ)'
        UNPAID = 'U', 'Unpaid (ຍັງບໍ່ຈ່າຍ)'
        PARTIAL = 'T', 'Partial (ຈ່າຍແລ້ວບາງສ່ວນ)'

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='tuition_fees')
    month = models.CharField(max_length=7, help_text="MM/YYYY e.g., 04/2026")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="ຈຳນວນເງິນຄ່າຮຽນ (ເຊັ່ນ: 500,000 ກີບ)")
    status = models.CharField(max_length=1, choices=FeeStatus.choices, default=FeeStatus.UNPAID)
    due_date = models.DateField(blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Tuition Fee (ຄ່າຮຽນ)"
        verbose_name_plural = "Tuition Fees (ບັນທຶກສະຖານະຈ່າຍຄ່າຮຽນ)"

    def __str__(self):
        return f"{self.enrollment.student} - {self.month} - {self.get_status_display()}"
