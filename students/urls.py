from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('search/', views.student_search, name='search'),
    path('new/', views.student_create, name='create'),
    path('import/', views.student_import, name='import'),
    path('export/', views.student_export, name='export'),
    path('<int:pk>/enrollments/', views.student_enrollments, name='enrollments'),
    path('<int:pk>/transfer/', views.student_transfer, name='transfer'),
    path('<int:pk>/edit/', views.student_update, name='update'),
    path('<int:pk>/delete/', views.student_delete, name='delete'),
]
