from django import forms
from django.contrib.auth.models import User
from .models import Workstation, WorkOrder


class WorkstationForm(forms.ModelForm):
    class Meta:
        model = Workstation
        fields = ['code', 'name', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['number', 'product_name', 'description', 'planned_quantity',
                  'start_date', 'end_date', 'status', 'workstation', 'assigned_workers']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'planned_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'workstation': forms.Select(attrs={'class': 'form-select'}),
            'assigned_workers': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['workstation'].queryset = Workstation.objects.filter(is_active=True)
        self.fields['assigned_workers'].help_text = 'Ctrl tusuna basarak birden fazla isci secebilirsiniz.'

        if user and hasattr(user, 'profile'):
            if user.profile.role == 'MANAGER':
                workers = User.objects.filter(
                    profile__manager=user, profile__role='WORKER', is_active=True
                ).select_related('profile')
            else:
                workers = User.objects.filter(
                    profile__role='WORKER', is_active=True
                ).select_related('profile')
            self.fields['assigned_workers'].queryset = workers
            self.fields['assigned_workers'].label_from_instance = (
                lambda u: f"{u.get_full_name()} ({u.profile.employee_id})"
            )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('Bitis tarihi baslangic tarihinden once olamaz.')
        return cleaned_data
