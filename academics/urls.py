from django.urls import path

from . import views

app_name = 'academics'

urlpatterns = [
    path('classes/', views.classroom_list, name='classrooms'),
    path('classes/new/', views.classroom_create, name='classroom_create'),
    path('classes/<int:pk>/edit/', views.classroom_update, name='classroom_update'),
    path('classes/<int:pk>/delete/', views.classroom_delete, name='classroom_delete'),
    path('subjects/', views.subject_list, name='subjects'),
    path('subjects/new/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
]
