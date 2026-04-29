from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("students/", views.students_collection, name="students_collection"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("classrooms/", views.classrooms_collection, name="classrooms_collection"),
    path("subjects/", views.subjects_collection, name="subjects_collection"),
    path("attendance/", views.attendance_collection, name="attendance_collection"),
    path("grades/", views.grades_collection, name="grades_collection"),
]
