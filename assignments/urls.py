from django.urls import path

from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.assignment_list, name='list'),
    path('create/', views.create_assignment, name='create'),
    path('<int:pk>/', views.assignment_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_assignment, name='edit'),
    path('<int:pk>/delete/', views.delete_assignment, name='delete'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit'),
]
