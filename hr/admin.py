from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
import uuid
from .models import HourlyRateRole, EmployeeProfile, Timesheet, PayrollSummary

@admin.register(HourlyRateRole)
class HourlyRateRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate_per_hour')

class EmployeeProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label="ຊື່ພະນັກງານ (First Name)")
    last_name = forms.CharField(max_length=150, label="ນາມສະກຸນ (Last Name)", required=False)

    class Meta:
        model = EmployeeProfile
        fields = (
            'first_name', 'last_name',
            'full_name_en',
            'nickname_en', 'nickname_lo',
            'age',
            'profile_image', 'phone_number', 'role',
            'education_background', 'previous_workplace', 'work_experience',
        )
        widgets = {
            'education_background': forms.Textarea(attrs={'rows': 3}),
            'previous_workplace': forms.Textarea(attrs={'rows': 3}),
            'work_experience': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'instance') and self.instance.pk and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        fname = self.cleaned_data.get('first_name', '')
        lname = self.cleaned_data.get('last_name', '')

        if getattr(profile, 'user_id', None) is None:
            username = f"emp_{uuid.uuid4().hex[:6]}"
            new_user = User.objects.create_user(
                username=username,
                first_name=fname,
                last_name=lname,
                password=uuid.uuid4().hex
            )
            profile.user = new_user
        else:
            profile.user.first_name = fname
            profile.user.last_name = lname
            profile.user.save()

        if commit:
            profile.save()
        return profile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    form = EmployeeProfileForm
    list_display = ('get_full_name', 'phone_number', 'role')
    search_fields = ('user__first_name', 'user__last_name', 'phone_number')

    def get_full_name(self, obj):
        name = obj.user.get_full_name()
        return name if name else obj.user.username
    get_full_name.short_description = "ຊື່ພະນັກງານ (Name)"

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'hours_worked', 'remark')
    list_filter = ('date', 'employee')
    date_hierarchy = 'date'

@admin.register(PayrollSummary)
class PayrollSummaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month_year', 'total_hours', 'total_amount', 'is_paid')
    list_filter = ('month_year', 'is_paid')
    search_fields = ('employee__user__first_name',)
