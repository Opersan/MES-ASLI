from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q

from .models import Workstation, WorkOrder, LaborEntry, DowntimeRecord, DowntimeReason
from .forms import WorkstationForm, WorkOrderForm
from accounts.decorators import role_required


def get_team_workers(user):
    return User.objects.filter(profile__manager=user, is_active=True)


# --- Dashboard ---

@login_required
def dashboard(request):
    user = request.user
    if not hasattr(user, 'profile'):
        messages.error(request, 'Kullanici profiliniz tanimli degil.')
        return redirect('logout')

    profile = user.profile

    if profile.role == 'WORKER':
        return redirect('production_screen')

    now = timezone.now()
    context = {'profile': profile}

    if profile.role == 'ADMIN':
        context.update({
            'total_users': User.objects.filter(is_active=True).count(),
            'total_work_orders': WorkOrder.objects.count(),
            'active_work_orders': WorkOrder.objects.filter(status='ACTIVE').count(),
            'open_downtimes': DowntimeRecord.objects.filter(status='OPEN').count(),
            'month_labor_minutes': LaborEntry.objects.filter(
                date__year=now.year, date__month=now.month, status='COMPLETED'
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0,
        })
    elif profile.role == 'MANAGER':
        team = get_team_workers(user)
        context.update({
            'team_count': team.count(),
            'active_work_orders': WorkOrder.objects.filter(
                Q(assigned_workers__in=team) | Q(created_by=user),
                status='ACTIVE'
            ).distinct().count(),
            'month_produced': LaborEntry.objects.filter(
                worker__in=team, date__year=now.year, date__month=now.month, status='COMPLETED'
            ).aggregate(total=Sum('produced_quantity'))['total'] or 0,
            'month_downtime_minutes': DowntimeRecord.objects.filter(
                worker__in=team, start_time__year=now.year, start_time__month=now.month,
                status='CLOSED'
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0,
            'recent_labor': LaborEntry.objects.filter(
                worker__in=team
            ).select_related('worker', 'work_order', 'workstation')[:10],
        })

    return render(request, 'production/dashboard.html', context)


# --- Production Screen ---

@login_required
def production_screen(request):
    profile = request.user.profile

    if profile.role == 'WORKER':
        work_orders = WorkOrder.objects.filter(
            assigned_workers=request.user, status='ACTIVE'
        ).select_related('workstation')
        active_labor = LaborEntry.objects.filter(
            worker=request.user, status='ACTIVE'
        ).select_related('work_order', 'workstation').first()
        active_downtime = None
        if active_labor:
            active_downtime = DowntimeRecord.objects.filter(
                labor_entry=active_labor, status='OPEN'
            ).select_related('reason').first()

        cards = []
        for wo in work_orders:
            labor = active_labor if (active_labor and active_labor.work_order_id == wo.pk) else None
            downtime = active_downtime if labor else None
            state = 'DOWNTIME' if downtime else ('WORKING' if labor else 'IDLE')
            total_produced = wo.labor_entries.filter(status='COMPLETED').aggregate(
                total=Sum('produced_quantity'))['total'] or 0
            progress = min(100, int(total_produced * 100 / wo.planned_quantity)) if wo.planned_quantity else 0
            cards.append({
                'work_order': wo,
                'labor': labor,
                'downtime': downtime,
                'state': state,
                'total_produced': total_produced,
                'progress': progress,
                'active_workers': [labor.worker] if labor else [],
            })
        has_active_labor = active_labor is not None

    elif profile.role == 'MANAGER':
        team = get_team_workers(request.user)
        work_orders = WorkOrder.objects.filter(
            Q(assigned_workers__in=team) | Q(created_by=request.user),
            status='ACTIVE'
        ).distinct().select_related('workstation')
        cards = []
        for wo in work_orders:
            active_labors = list(LaborEntry.objects.filter(
                work_order=wo, status='ACTIVE'
            ).select_related('worker', 'workstation'))
            active_workers = [l.worker for l in active_labors]
            first_labor = active_labors[0] if active_labors else None
            first_downtime = None
            has_dt = False
            if first_labor:
                first_downtime = DowntimeRecord.objects.filter(
                    labor_entry=first_labor, status='OPEN'
                ).select_related('reason').first()
                has_dt = first_downtime is not None
            state = 'DOWNTIME' if has_dt else ('WORKING' if active_workers else 'IDLE')
            total_produced = wo.labor_entries.filter(status='COMPLETED').aggregate(
                total=Sum('produced_quantity'))['total'] or 0
            progress = min(100, int(total_produced * 100 / wo.planned_quantity)) if wo.planned_quantity else 0
            cards.append({
                'work_order': wo,
                'labor': first_labor,
                'downtime': first_downtime,
                'state': state,
                'total_produced': total_produced,
                'progress': progress,
                'active_workers': active_workers,
            })
        has_active_labor = False

    else:  # ADMIN
        work_orders = WorkOrder.objects.filter(status='ACTIVE').select_related('workstation')
        cards = []
        for wo in work_orders:
            active_labors = list(LaborEntry.objects.filter(
                work_order=wo, status='ACTIVE'
            ).select_related('worker', 'workstation'))
            active_workers = [l.worker for l in active_labors]
            first_labor = active_labors[0] if active_labors else None
            first_downtime = None
            has_dt = False
            if first_labor:
                first_downtime = DowntimeRecord.objects.filter(
                    labor_entry=first_labor, status='OPEN'
                ).select_related('reason').first()
                has_dt = first_downtime is not None
            state = 'DOWNTIME' if has_dt else ('WORKING' if active_workers else 'IDLE')
            total_produced = wo.labor_entries.filter(status='COMPLETED').aggregate(
                total=Sum('produced_quantity'))['total'] or 0
            progress = min(100, int(total_produced * 100 / wo.planned_quantity)) if wo.planned_quantity else 0
            cards.append({
                'work_order': wo,
                'labor': first_labor,
                'downtime': first_downtime,
                'state': state,
                'total_produced': total_produced,
                'progress': progress,
                'active_workers': active_workers,
            })
        has_active_labor = False

    reasons = DowntimeReason.objects.all()
    return render(request, 'production/production_screen.html', {
        'cards': cards,
        'profile': profile,
        'reasons': reasons,
        'has_active_labor': has_active_labor,
    })


@login_required
@role_required('WORKER')
def start_labor(request, pk):
    if request.method != 'POST':
        return redirect('production_screen')

    wo = get_object_or_404(WorkOrder, pk=pk, status='ACTIVE')
    if request.user not in wo.assigned_workers.all():
        messages.error(request, 'Bu is emrine yetkiniz yok.')
        return redirect('production_screen')

    existing = LaborEntry.objects.filter(worker=request.user, status='ACTIVE').first()
    if existing:
        messages.warning(request, 'Zaten aktif bir iscilik kaydiniz var.')
        return redirect('production_screen')

    now = timezone.now()
    LaborEntry.objects.create(
        work_order=wo,
        worker=request.user,
        workstation=wo.workstation,
        start_time=now,
        date=now.date(),
        status='ACTIVE',
    )
    messages.success(request, f'{wo.number} uzerinde uretim baslatildi.')
    return redirect('production_screen')


@login_required
@role_required('WORKER')
def stop_labor(request, pk):
    labor = get_object_or_404(LaborEntry, pk=pk, worker=request.user, status='ACTIVE')

    if request.method == 'POST':
        produced = request.POST.get('produced_quantity', '0')
        desc = request.POST.get('description', '')
        completion = request.POST.get('completion_type', 'partial')

        try:
            produced = max(0, int(produced))
        except (ValueError, TypeError):
            produced = 0

        # Close any open downtime first
        open_dt = DowntimeRecord.objects.filter(labor_entry=labor, status='OPEN').first()
        if open_dt:
            open_dt.end_time = timezone.now()
            diff = open_dt.end_time - open_dt.start_time
            open_dt.duration_minutes = max(0, int(diff.total_seconds() / 60))
            open_dt.status = 'CLOSED'
            open_dt.save()

        now = timezone.now()
        labor.end_time = now
        labor.produced_quantity = produced
        labor.description = desc
        labor.status = 'COMPLETED'
        labor.save()

        if completion == 'complete':
            labor.work_order.status = 'COMPLETED'
            labor.work_order.save()
            messages.success(request, f'{labor.work_order.number} tamamlandi.')
        else:
            messages.success(request, 'Uretim durduruldu, iscilik kaydedildi.')
        return redirect('production_screen')

    return render(request, 'production/stop_labor.html', {'labor': labor})


@login_required
@role_required('WORKER')
def production_start_downtime(request, pk):
    if request.method != 'POST':
        return redirect('production_screen')

    labor = get_object_or_404(LaborEntry, pk=pk, worker=request.user, status='ACTIVE')

    existing = DowntimeRecord.objects.filter(labor_entry=labor, status='OPEN').first()
    if existing:
        messages.warning(request, 'Bu iscilik kaydinda zaten acik durus var.')
        return redirect('production_screen')

    reason_id = request.POST.get('reason')
    desc = request.POST.get('description', '')
    reason = get_object_or_404(DowntimeReason, pk=reason_id)

    DowntimeRecord.objects.create(
        worker=request.user,
        work_order=labor.work_order,
        workstation=labor.workstation,
        labor_entry=labor,
        start_time=timezone.now(),
        reason=reason,
        description=desc,
        status='OPEN',
    )
    messages.success(request, f'Durus baslatildi: {reason.name}')
    return redirect('production_screen')


@login_required
@role_required('WORKER')
def production_stop_downtime(request, pk):
    if request.method != 'POST':
        return redirect('production_screen')

    record = get_object_or_404(DowntimeRecord, pk=pk, worker=request.user, status='OPEN')
    record.end_time = timezone.now()
    diff = record.end_time - record.start_time
    record.duration_minutes = max(0, int(diff.total_seconds() / 60))
    record.status = 'CLOSED'
    record.save()
    messages.success(request, 'Durus kapatildi.')
    return redirect('production_screen')


# --- Workstation ---

@login_required
@role_required('ADMIN', 'MANAGER')
def workstation_list(request):
    workstations = Workstation.objects.all()
    return render(request, 'production/workstation_list.html', {'workstations': workstations})


@login_required
@role_required('ADMIN', 'MANAGER')
def workstation_create(request):
    if request.method == 'POST':
        form = WorkstationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Is istasyonu basariyla olusturuldu.')
            return redirect('workstation_list')
    else:
        form = WorkstationForm()
    return render(request, 'production/workstation_form.html', {'form': form, 'title': 'Is Istasyonu Ekle'})


@login_required
@role_required('ADMIN', 'MANAGER')
def workstation_edit(request, pk):
    workstation = get_object_or_404(Workstation, pk=pk)
    if request.method == 'POST':
        form = WorkstationForm(request.POST, instance=workstation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Is istasyonu guncellendi.')
            return redirect('workstation_list')
    else:
        form = WorkstationForm(instance=workstation)
    return render(request, 'production/workstation_form.html', {'form': form, 'title': 'Is Istasyonu Duzenle'})


# --- WorkOrder ---

@login_required
@role_required('ADMIN', 'MANAGER')
def workorder_list(request):
    profile = request.user.profile
    if profile.role == 'ADMIN':
        orders = WorkOrder.objects.all()
    else:
        team = get_team_workers(request.user)
        orders = WorkOrder.objects.filter(
            Q(assigned_workers__in=team) | Q(created_by=request.user)
        ).distinct()
    orders = orders.select_related('workstation', 'created_by')
    return render(request, 'production/workorder_list.html', {'orders': orders, 'profile': profile})


@login_required
@role_required('ADMIN', 'MANAGER')
def workorder_create(request):
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            form.save_m2m()
            messages.success(request, 'Is emri basariyla olusturuldu.')
            return redirect('workorder_detail', pk=order.pk)
    else:
        form = WorkOrderForm(user=request.user)
    return render(request, 'production/workorder_form.html', {'form': form, 'title': 'Is Emri Olustur'})


@login_required
def workorder_detail(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    profile = request.user.profile

    if profile.role == 'WORKER':
        if request.user not in order.assigned_workers.all():
            messages.error(request, 'Bu is emrine erisim yetkiniz yok.')
            return redirect('production_screen')
    elif profile.role == 'MANAGER':
        team = get_team_workers(request.user)
        has_team_worker = order.assigned_workers.filter(id__in=team).exists()
        if order.created_by != request.user and not has_team_worker:
            messages.error(request, 'Bu is emrine erisim yetkiniz yok.')
            return redirect('workorder_list')

    labor_entries = LaborEntry.objects.filter(work_order=order).select_related('worker', 'workstation')
    downtime_records = DowntimeRecord.objects.filter(work_order=order).select_related('worker', 'reason')
    total_produced = labor_entries.filter(status='COMPLETED').aggregate(total=Sum('produced_quantity'))['total'] or 0
    total_labor_minutes = labor_entries.filter(status='COMPLETED').aggregate(total=Sum('duration_minutes'))['total'] or 0

    return render(request, 'production/workorder_detail.html', {
        'order': order,
        'labor_entries': labor_entries,
        'downtime_records': downtime_records,
        'total_produced': total_produced,
        'total_labor_minutes': total_labor_minutes,
        'profile': profile,
    })


@login_required
@role_required('ADMIN', 'MANAGER')
def workorder_edit(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    profile = request.user.profile

    if profile.role == 'MANAGER' and order.created_by != request.user:
        messages.error(request, 'Sadece kendi olusturdgunuz is emirlerini duzenleyebilirsiniz.')
        return redirect('workorder_list')

    if request.method == 'POST':
        form = WorkOrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Is emri guncellendi.')
            return redirect('workorder_detail', pk=order.pk)
    else:
        form = WorkOrderForm(instance=order, user=request.user)
    return render(request, 'production/workorder_form.html', {'form': form, 'title': 'Is Emri Duzenle'})


# --- LaborEntry List ---

@login_required
@role_required('ADMIN', 'MANAGER')
def labor_entry_list(request):
    profile = request.user.profile
    if profile.role == 'ADMIN':
        entries = LaborEntry.objects.all()
    else:
        team = get_team_workers(request.user)
        entries = LaborEntry.objects.filter(worker__in=team)
    entries = entries.select_related('worker', 'work_order', 'workstation')
    return render(request, 'production/labor_entry_list.html', {'entries': entries, 'profile': profile})


# --- DowntimeRecord List ---

@login_required
@role_required('ADMIN', 'MANAGER')
def downtime_list(request):
    profile = request.user.profile
    if profile.role == 'ADMIN':
        records = DowntimeRecord.objects.all()
    else:
        team = get_team_workers(request.user)
        records = DowntimeRecord.objects.filter(worker__in=team)
    records = records.select_related('worker', 'work_order', 'workstation', 'reason')
    return render(request, 'production/downtime_list.html', {'records': records, 'profile': profile})
