from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Production screen
    path('production/', views.production_screen, name='production_screen'),
    path('production/labor/start/<int:pk>/', views.start_labor, name='start_labor'),
    path('production/labor/<int:pk>/stop/', views.stop_labor, name='stop_labor'),
    path('production/labor/<int:pk>/downtime/start/', views.production_start_downtime, name='production_start_downtime'),
    path('production/downtime/<int:pk>/stop/', views.production_stop_downtime, name='production_stop_downtime'),
    # CRUD
    path('workstations/', views.workstation_list, name='workstation_list'),
    path('workstations/create/', views.workstation_create, name='workstation_create'),
    path('workstations/<int:pk>/edit/', views.workstation_edit, name='workstation_edit'),
    path('workorders/', views.workorder_list, name='workorder_list'),
    path('workorders/create/', views.workorder_create, name='workorder_create'),
    path('workorders/<int:pk>/', views.workorder_detail, name='workorder_detail'),
    path('workorders/<int:pk>/edit/', views.workorder_edit, name='workorder_edit'),
    path('labor/', views.labor_entry_list, name='labor_entry_list'),
    path('downtime/', views.downtime_list, name='downtime_list'),
]
