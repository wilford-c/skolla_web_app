from django.urls import path

from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('new/', views.attendance_mark, name='create'),
    path('reports/', views.attendance_reports, name='reports'),
    path('reports/export/csv/', views.attendance_export_csv, name='export_csv'),
    path('reports/export/pdf/', views.attendance_export_pdf, name='export_pdf'),
    path('reports/builder/', views.report_builder, name='report_builder'),
    path('reports/templates/', views.template_list, name='template_list'),
    path('reports/templates/<int:pk>/edit/', views.template_update, name='template_update'),
    path('reports/templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('records/<int:pk>/edit/', views.attendance_update, name='update'),
    path('records/<int:pk>/delete/', views.attendance_delete, name='delete'),
    path('notifications/', views.notification_preferences, name='notification_preferences'),
]
