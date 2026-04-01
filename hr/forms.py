from django import forms
from .models import Timesheet, PayrollSummary

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['employee', 'date', 'hours_worked', 'remark']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hours_worked': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'remark': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].widget.attrs.update({'class': 'form-select'})

class PayrollSummaryForm(forms.ModelForm):
    class Meta:
        model = PayrollSummary
        fields = ['employee', 'month_year', 'total_hours', 'total_amount', 'is_paid', 'notes']
        widgets = {
            'month_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YYYY'}),
        }

from django.contrib.auth.models import User
from .models import EmployeeProfile, HourlyRateRole
import uuid

class EmployeeProfileWebForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label="ຊື່ພະນັກງານ (First Name)", widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2 px-3'}))
    last_name = forms.CharField(max_length=150, label="ນາມສະກຸນ (Last Name)", required=False, widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2 px-3'}))
    phone_number = forms.CharField(max_length=20, label="ເບີໂທຕິດຕໍ່ (Phone Number)", required=False, widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2 px-3'}))
    role = forms.ModelChoiceField(queryset=HourlyRateRole.objects.all(), required=False, label="ຕຳແໜ່ງ (Role / Hourly Rate)", widget=forms.Select(attrs={'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2 px-3'}))

    class Meta:
        model = EmployeeProfile
        fields = ['first_name', 'last_name', 'phone_number', 'role']
        
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
