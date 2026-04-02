from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Kullanıcı Adı',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kullanıcı adınız'})
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Şifreniz'})
    )
