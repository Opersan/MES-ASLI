import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from production.models import LaborEntry, DowntimeRecord
from accounts.decorators import role_required


def get_team_workers(user):
    return User.objects.filter(profile__manager=user, is_active=True)


@login_required
@role_required('ADMIN', 'MANAGER')
def monthly_report(request):
    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    export_csv = request.GET.get('export') == 'csv'
    profile = request.user.profile

    labor_qs = LaborEntry.objects.filter(date__year=year, date__month=month)
    downtime_qs = DowntimeRecord.objects.filter(
        start_time__year=year, start_time__month=month, status='CLOSED'
    )

    if profile.role == 'MANAGER':
        team = get_team_workers(request.user)
        labor_qs = labor_qs.filter(worker__in=team)
        downtime_qs = downtime_qs.filter(worker__in=team)

    labor_by_worker = labor_qs.values(
        'worker__first_name', 'worker__last_name', 'worker__profile__employee_id'
    ).annotate(
        total_duration=Sum('duration_minutes'),
        total_produced=Sum('produced_quantity'),
    ).order_by('worker__last_name')

    downtime_by_reason = downtime_qs.values('reason__name').annotate(
        total_duration=Sum('duration_minutes')
    ).order_by('reason__name')

    downtime_by_workstation = downtime_qs.values(
        'workstation__code', 'workstation__name'
    ).annotate(
        total_duration=Sum('duration_minutes')
    ).order_by('workstation__code')

    labor_by_workorder = labor_qs.values(
        'work_order__number', 'work_order__product_name'
    ).annotate(
        total_duration=Sum('duration_minutes'),
        total_produced=Sum('produced_quantity'),
    ).order_by('work_order__number')

    if export_csv:
        return _export_csv(labor_by_worker, downtime_by_reason,
                           downtime_by_workstation, labor_by_workorder, year, month)

    context = {
        'year': year,
        'month': month,
        'years': range(now.year - 2, now.year + 1),
        'months': range(1, 13),
        'labor_by_worker': labor_by_worker,
        'downtime_by_reason': downtime_by_reason,
        'downtime_by_workstation': downtime_by_workstation,
        'labor_by_workorder': labor_by_workorder,
        'profile': profile,
    }
    return render(request, 'reports/monthly_report.html', context)


def _export_csv(labor_by_worker, downtime_by_reason,
                downtime_by_workstation, labor_by_workorder, year, month):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="rapor_{year}_{month:02d}.csv"'
    response.write('\ufeff')  # BOM for Excel
    writer = csv.writer(response, delimiter=';')

    writer.writerow(['İŞÇİ BAZLI İŞÇİLİK'])
    writer.writerow(['Sicil No', 'Ad Soyad', 'Toplam Süre (dk)', 'Toplam Üretim'])
    for row in labor_by_worker:
        writer.writerow([
            row['worker__profile__employee_id'],
            f"{row['worker__first_name']} {row['worker__last_name']}",
            row['total_duration'] or 0,
            row['total_produced'] or 0,
        ])

    writer.writerow([])
    writer.writerow(['DURUŞ NEDENİ BAZLI'])
    writer.writerow(['Neden', 'Toplam Süre (dk)'])
    for row in downtime_by_reason:
        writer.writerow([row['reason__name'], row['total_duration'] or 0])

    writer.writerow([])
    writer.writerow(['İSTASYON BAZLI DURUŞ'])
    writer.writerow(['Kod', 'İstasyon', 'Toplam Süre (dk)'])
    for row in downtime_by_workstation:
        writer.writerow([
            row['workstation__code'], row['workstation__name'],
            row['total_duration'] or 0,
        ])

    writer.writerow([])
    writer.writerow(['İŞ EMRİ BAZLI İŞÇİLİK'])
    writer.writerow(['İş Emri No', 'Ürün', 'Toplam Süre (dk)', 'Toplam Üretim'])
    for row in labor_by_workorder:
        writer.writerow([
            row['work_order__number'], row['work_order__product_name'],
            row['total_duration'] or 0, row['total_produced'] or 0,
        ])

    return response
