from django.urls import path

from . import views

app_name = 'calendar'

urlpatterns = [
    path('', views.calendar_view, name='index'),
    path('feed.ics', views.calendar_ical_feed, name='ical_feed'),
]
