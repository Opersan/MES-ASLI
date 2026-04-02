from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Workstation(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Kod')
    name = models.CharField(max_length=100, verbose_name='Ad')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'İş İstasyonu'
        verbose_name_plural = 'İş İstasyonları'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('ACTIVE', 'Aktif'),
        ('COMPLETED', 'Tamamlandı'),
        ('CANCELLED', 'İptal'),
    ]

    number = models.CharField(max_length=50, unique=True, verbose_name='Numara')
    product_name = models.CharField(max_length=200, verbose_name='Ürün Adı')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    planned_quantity = models.PositiveIntegerField(verbose_name='Planlanan Adet')
    start_date = models.DateField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateField(verbose_name='Bitiş Tarihi')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT', verbose_name='Durum')
    workstation = models.ForeignKey(
        Workstation, on_delete=models.PROTECT, verbose_name='İş İstasyonu'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='created_work_orders', verbose_name='Oluşturan'
    )
    assigned_workers = models.ManyToManyField(
        User, blank=True, related_name='assigned_work_orders', verbose_name='Atanan İşçiler'
    )

    class Meta:
        verbose_name = 'İş Emri'
        verbose_name_plural = 'İş Emirleri'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.number} - {self.product_name}"

    @property
    def total_produced(self):
        return self.labor_entries.filter(status='COMPLETED').aggregate(
            total=models.Sum('produced_quantity')
        )['total'] or 0


class DowntimeReason(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name='Kod')
    name = models.CharField(max_length=100, verbose_name='Ad')
    description = models.TextField(blank=True, verbose_name='Açıklama')

    class Meta:
        verbose_name = 'Duruş Nedeni'
        verbose_name_plural = 'Duruş Nedenleri'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class LaborEntry(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Aktif'),
        ('COMPLETED', 'Tamamlandı'),
    ]

    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.PROTECT, related_name='labor_entries', verbose_name='İş Emri'
    )
    worker = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='labor_entries', verbose_name='İşçi'
    )
    workstation = models.ForeignKey(
        Workstation, on_delete=models.PROTECT, verbose_name='İş İstasyonu'
    )
    start_time = models.DateTimeField(verbose_name='Başlangıç Zamanı')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş Zamanı')
    date = models.DateField(verbose_name='Tarih')
    produced_quantity = models.PositiveIntegerField(default=0, verbose_name='Üretilen Adet')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name='Süre (dk)', editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE', verbose_name='Durum')

    class Meta:
        verbose_name = 'İşçilik Kaydı'
        verbose_name_plural = 'İşçilik Kayıtları'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.worker.get_full_name()} - {self.work_order.number} - {self.date}"

    def save(self, *args, **kwargs):
        if self.start_time:
            self.date = self.start_time.date()
        if self.start_time and self.end_time:
            diff = self.end_time - self.start_time
            self.duration_minutes = max(0, int(diff.total_seconds() / 60))
        super().save(*args, **kwargs)

    @property
    def duration_display(self):
        if self.status == 'ACTIVE' and self.start_time:
            diff = timezone.now() - self.start_time
            total = max(0, int(diff.total_seconds() / 60))
        else:
            total = self.duration_minutes
        return f"{total // 60} sa {total % 60} dk"

    @property
    def elapsed_seconds(self):
        if self.status == 'ACTIVE' and self.start_time:
            return max(0, int((timezone.now() - self.start_time).total_seconds()))
        return self.duration_minutes * 60


class DowntimeRecord(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Açık'),
        ('CLOSED', 'Kapalı'),
    ]

    worker = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='downtime_records', verbose_name='İşçi'
    )
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.PROTECT, related_name='downtime_records', verbose_name='İş Emri'
    )
    workstation = models.ForeignKey(
        Workstation, on_delete=models.PROTECT, verbose_name='İş İstasyonu'
    )
    labor_entry = models.ForeignKey(
        'LaborEntry', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='downtime_records', verbose_name='İşçilik Kaydı'
    )
    start_time = models.DateTimeField(verbose_name='Başlangıç Zamanı')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş Zamanı')
    reason = models.ForeignKey(
        DowntimeReason, on_delete=models.PROTECT, verbose_name='Duruş Nedeni'
    )
    description = models.TextField(blank=True, verbose_name='Açıklama')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN', verbose_name='Durum')
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name='Süre (dk)', editable=False)

    class Meta:
        verbose_name = 'Duruş Kaydı'
        verbose_name_plural = 'Duruş Kayıtları'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.worker.get_full_name()} - {self.reason.name} - {self.start_time}"

    @property
    def elapsed_seconds(self):
        if self.status == 'OPEN' and self.start_time:
            return max(0, int((timezone.now() - self.start_time).total_seconds()))
        return self.duration_minutes * 60

    @property
    def duration_display(self):
        hours = self.duration_minutes // 60
        mins = self.duration_minutes % 60
        return f"{hours} sa {mins} dk"
