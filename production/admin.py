from django.contrib import admin
from .models import Workstation, WorkOrder, LaborEntry, DowntimeRecord, DowntimeReason


@admin.register(Workstation)
class WorkstationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'product_name', 'status', 'workstation', 'start_date', 'end_date', 'created_by']
    list_filter = ['status', 'workstation']
    search_fields = ['number', 'product_name']
    filter_horizontal = ['assigned_workers']


@admin.register(DowntimeReason)
class DowntimeReasonAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(LaborEntry)
class LaborEntryAdmin(admin.ModelAdmin):
    list_display = ['worker', 'work_order', 'workstation', 'date', 'start_time', 'end_time',
                    'produced_quantity', 'duration_minutes', 'status']
    list_filter = ['status', 'date', 'worker', 'workstation']
    search_fields = ['work_order__number']


@admin.register(DowntimeRecord)
class DowntimeRecordAdmin(admin.ModelAdmin):
    list_display = ['worker', 'work_order', 'reason', 'status', 'start_time', 'end_time',
                    'duration_minutes', 'labor_entry']
    list_filter = ['status', 'reason', 'worker']
    search_fields = ['work_order__number']
