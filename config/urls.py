from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("students/", include("students.urls")),
    path("academics/", include("academics.urls")),
    path("attendance/", include("attendance.urls")),
]
