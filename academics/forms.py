from django import forms
from .models import MonthlyScore, Enrollment, TuitionFee
import datetime


class TuitionFeeForm(forms.ModelForm):
    class Meta:
        model = TuitionFee
        fields = '__all__'




def get_month_choices():
    today = datetime.date.today()
    choices = [('', '--- ເລືອກເດືອນ ---')]
    # Generate ±12 months around today
    for i in range(-12, 13):
        m = today.month + i - 1
        y = today.year + m // 12
        m = m % 12 + 1
        dt = datetime.date(y, m, 1)
        m_str = dt.strftime('%m/%Y')
        m_label = dt.strftime('%b %Y')
        choices.append((m_str, m_label))
    return choices


class MonthlyScoreForm(forms.ModelForm):
    month = forms.ChoiceField(
        choices=get_month_choices,
        label="ເດືອນ (Month)",
        help_text="ເລືອກເດືອນທີ່ຕ້ອງການບັນທຶກຄະແນນ"
    )

    class Meta:
        model = MonthlyScore
        fields = [
            'enrollment', 'month',
            'engagement', 'attendance', 'monthly_test', 'exercise',
            'remark',
        ]
        labels = {
            'enrollment': 'ນັກຮຽນ / ຫ້ອງ',
            'engagement': 'ACTIVITY / ກິດຈະກຳ (/30)  — 30%',
            'attendance': 'ATTENDANCE / ເຂົ້າຮຽນ (/20)  — 20%',
            'monthly_test': 'QUIZ / Monthly Test (/30)  — 30%',
            'exercise': 'Exercise / Assignment (/20)  — 20%',
            'remark': 'ໝາຍເຫດ',
        }
        widgets = {
            'remark': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, class_schedule_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if class_schedule_id:
            self.fields['enrollment'].queryset = (
                Enrollment.objects
                .filter(class_schedule_id=class_schedule_id)
                .select_related('student')
            )
        self.fields['enrollment'].label_from_instance = (
            lambda obj: f"{obj.student.full_name}  ({obj.student.nick_name or ''})"
        )


class MonthlyScoreBulkForm(forms.Form):
    """Used for the calendar-month bulk-entry page (one row per student)"""
    month = forms.ChoiceField(
        choices=get_month_choices,
        label="ເດືອນ (Month)",
    )
    class_schedule = forms.ModelChoiceField(
        queryset=None,
        label="ຫ້ອງຮຽນ (Class)",
        empty_label="--- ເລືອກຫ້ອງ ---"
    )

    def __init__(self, *args, schedules_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        from academics.models import ClassSchedule
        self.fields['class_schedule'].queryset = (
            schedules_qs if schedules_qs is not None
            else ClassSchedule.objects.select_related('course').filter(is_active=True)
        )
        self.fields['class_schedule'].label_from_instance = (
            lambda obj: f"{obj.course.name} — {obj.time_slot}"
        )
