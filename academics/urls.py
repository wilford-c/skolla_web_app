from django.urls import path

from . import views

app_name = 'academics'

urlpatterns = [
    # Classrooms
    path('classes/', views.classroom_list, name='classrooms'),
    path('classes/new/', views.classroom_create, name='classroom_create'),
    path('classes/<int:pk>/edit/', views.classroom_update, name='classroom_update'),
    path('classes/<int:pk>/delete/', views.classroom_delete, name='classroom_delete'),
    
    # Subjects
    path('subjects/', views.subject_list, name='subjects'),
    path('subjects/new/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Assessments
    path('assessments/', views.assessment_list, name='assessments'),
    path('assessments/new/', views.assessment_create, name='assessment_create'),
    path('assessments/<int:pk>/edit/', views.assessment_update, name='assessment_update'),
    path('assessments/<int:pk>/delete/', views.assessment_delete, name='assessment_delete'),
    
    # Grades
    path('grades/', views.grade_list, name='grades'),
    path('grades/new/', views.grade_create, name='grade_create'),
    path('grades/bulk/', views.grade_bulk_entry, name='grade_bulk_entry'),
    path('grades/<int:pk>/edit/', views.grade_update, name='grade_update'),
    path('grades/<int:pk>/delete/', views.grade_delete, name='grade_delete'),
    
    # Student grade view
    path('student-grades/', views.student_grades, name='student_grades'),
    path('student-grades/<int:student_id>/', views.student_grades, name='student_grades_detail'),
]
