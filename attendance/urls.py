from django.urls import path

from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('new/', views.attendance_mark, name='create'),
    path('records/<int:pk>/edit/', views.attendance_update, name='update'),
    path('records/<int:pk>/delete/', views.attendance_delete, name='delete'),
]
