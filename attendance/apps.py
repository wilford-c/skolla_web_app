from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    name = 'attendance'
    
    def ready(self):
        """Import signals when app is ready."""
        import attendance.signals  # noqa: F401
