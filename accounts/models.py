from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Yönetici'),
        ('WORKER', 'İşçi'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='Sicil No')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='Rol')
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='team_members', verbose_name='Yönetici'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profiller'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
