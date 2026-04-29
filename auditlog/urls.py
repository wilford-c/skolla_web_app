from django.urls import path

from . import views

app_name = "auditlog"

urlpatterns = [
    path("", views.audit_event_list, name="list"),
]
