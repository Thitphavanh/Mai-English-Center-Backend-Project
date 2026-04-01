from django.contrib import admin
from .models import (
    Course, ClassSchedule, Student, Enrollment, 
    DailyChecklist, Assessment, AssessmentCriteria, 
    AssessmentDetail, TuitionFee
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'book_name', 'created_at')
    search_fields = ('name', 'book_name')

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'time_slot', 'start_date', 'is_active')
    list_filter = ('is_active', 'teacher')
    search_fields = ('course__name', 'time_slot')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'nick_name', 'phone_number')
    search_fields = ('student_id', 'full_name', 'nick_name', 'phone_number')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_schedule', 'enrollment_date')
    list_filter = ('class_schedule',)
    search_fields = ('student__full_name', 'class_schedule__course__name')

@admin.register(DailyChecklist)
class DailyChecklistAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'date', 'status', 'score')
    list_filter = ('date', 'status')
    search_fields = ('enrollment__student__full_name',)

class AssessmentDetailInline(admin.TabularInline):
    model = AssessmentDetail
    extra = 1

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'evaluator', 'total_score', 'gpa', 'evaluation_date')
    inlines = [AssessmentDetailInline]
    list_filter = ('evaluation_date',)
    search_fields = ('enrollment__student__full_name',)

@admin.register(AssessmentCriteria)
class AssessmentCriteriaAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_lo', 'category', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(TuitionFee)
class TuitionFeeAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'month', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'month')
    search_fields = ('enrollment__student__full_name',)

    def get_student(self, obj):
        return obj.enrollment.student.full_name
    get_student.short_description = 'Student'
