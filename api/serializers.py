from rest_framework import serializers
from academics.models import Student, Enrollment, Assessment, MonthlyScore, DailyChecklist, TuitionFee, ClassSchedule
from hr.models import EmployeeProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'is_staff']

class ClassScheduleSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    book_name = serializers.CharField(source='course.book_name', read_only=True)
    
    class Meta:
        model = ClassSchedule
        fields = ['id', 'course_name', 'book_name', 'time_slot']

class TeacherProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    nick_names = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    workplace = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    teaching_classes = ClassScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'nick_names', 'profile_image', 
            'phone_number', 'age', 'education', 'workplace', 'experience', 
            'teaching_classes'
        ]

    def _get_profile(self, obj):
        return getattr(obj, 'employee_profile', None)

    def get_full_name(self, obj):
        profile = self._get_profile(obj)
        if profile and profile.full_name_en:
            return profile.full_name_en
        return obj.get_full_name() or obj.username

    def get_nick_names(self, obj):
        profile = self._get_profile(obj)
        if profile:
            names = []
            if profile.nickname_en: names.append(f'"{profile.nickname_en}"')
            if profile.nickname_lo: names.append(f'"{profile.nickname_lo}"')
            return " ".join(names)
        return ""

    def get_profile_image(self, obj):
        profile = self._get_profile(obj)
        request = self.context.get('request')
        if profile and profile.profile_image and request:
            return request.build_absolute_uri(profile.profile_image.url)
        return None

    def get_phone_number(self, obj):
        profile = self._get_profile(obj)
        return profile.phone_number if profile else ""

    def get_age(self, obj):
        profile = self._get_profile(obj)
        return profile.age if profile else None

    def get_education(self, obj):
        profile = self._get_profile(obj)
        return profile.education_background if profile else ""

    def get_workplace(self, obj):
        profile = self._get_profile(obj)
        return profile.previous_workplace if profile else ""

    def get_experience(self, obj):
        profile = self._get_profile(obj)
        return profile.work_experience if profile else ""

class DailyChecklistSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DailyChecklist
        fields = ['date', 'status', 'status_display', 'remark']

class TuitionFeeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount = serializers.FloatField()
    
    class Meta:
        model = TuitionFee
        fields = ['month', 'amount', 'status', 'status_display', 'due_date', 'payment_date', 'note']

class AssessmentSerializer(serializers.ModelSerializer):
    total_score = serializers.FloatField()
    gpa = serializers.FloatField()
    
    class Meta:
        model = Assessment
        fields = ['total_score', 'letter_grade', 'gpa', 'general_remarks']

class MonthlyScoreSerializer(serializers.ModelSerializer):
    general_remarks = serializers.CharField(source='remark', read_only=True)
    total_score = serializers.FloatField()
    gpa = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyScore
        fields = ['total_score', 'letter_grade', 'gpa', 'general_remarks']

    def get_gpa(self, obj):
        grade_map = {'A': 4.0, 'B+': 3.5, 'C+': 2.5, 'D': 1.5, 'F': 0.0}
        return grade_map.get(obj.letter_grade, 0.0)

class EnrollmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='class_schedule.course.name', read_only=True)
    time_slot = serializers.CharField(source='class_schedule.time_slot', read_only=True)
    teacher_id = serializers.IntegerField(source='class_schedule.teacher.id', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    latest_assessment = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    tuition_fees = TuitionFeeSerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course_name', 'time_slot', 'teacher_id', 'teacher_name', 'latest_assessment', 'attendance', 'tuition_fees']

    def get_teacher_name(self, obj):
        teacher = obj.class_schedule.teacher
        if teacher:
            profile = getattr(teacher, 'employee_profile', None)
            if profile and profile.full_name_en:
                return f"ອ.ຈ {profile.full_name_en}"
            return f"ອ.ຈ {teacher.get_full_name() or teacher.username}"
        return None

    def get_latest_assessment(self, obj):
        latest = obj.get_latest_evaluation
        if not latest:
            return None
            
        if isinstance(latest, Assessment):
            return AssessmentSerializer(latest).data
        else:
            return MonthlyScoreSerializer(latest).data

    def get_attendance(self, obj):
        records = obj.daily_records.order_by('-date')[:5]
        return DailyChecklistSerializer(records, many=True).data

class StudentSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'full_name', 'nick_name', 'profile_image', 'enrollments']
        
    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None
