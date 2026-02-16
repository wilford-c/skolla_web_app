from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
]
