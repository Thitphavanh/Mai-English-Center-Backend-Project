from django import forms
from .models import TuitionFee

class TuitionFeeForm(forms.ModelForm):
    class Meta:
        model = TuitionFee
        fields = ['enrollment', 'month', 'amount', 'status', 'due_date', 'payment_date', 'note']
        widgets = {
            'enrollment': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YYYY (e.g. 04/2026)'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }
