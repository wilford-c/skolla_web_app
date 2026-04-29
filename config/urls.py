from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("", include("accounts.urls")),
    path("audit/", include("auditlog.urls")),
    path("students/", include("students.urls")),
    path("academics/", include("academics.urls")),
    path("attendance/", include("attendance.urls")),
    path("billing/", include("billing.urls")),
    path("announcements/", include("announcements.urls")),
    path("calendar/", include("calendar_events.urls")),
    path("assignments/", include("assignments.urls")),
    path("messages/", include("messaging.urls")),
    path("notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
