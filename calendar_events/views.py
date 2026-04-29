from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from datetime import date, timedelta

from .models import Event


@login_required
def calendar_view(request):
    """Display calendar of school events."""
    today = date.today()
    start_of_month = today.replace(day=1)
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=today
    ).order_by('start_date')[:10]
    
    # Get this month's events
    next_month = start_of_month + timedelta(days=32)
    next_month_start = next_month.replace(day=1)
    
    current_month_events = Event.objects.filter(
        start_date__gte=start_of_month,
        start_date__lt=next_month_start
    ).order_by('start_date')
    
    return render(request, 'calendar/index.html', {
        'upcoming_events': upcoming_events,
        'current_month_events': current_month_events,
        'current_month': start_of_month,
    })


@login_required
def calendar_ical_feed(request):
    """Export upcoming events in iCalendar format for external calendar apps."""
    today = date.today()
    events = Event.objects.filter(end_date__gte=today).order_by('start_date', 'start_time')[:500]

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Skola//School Calendar//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
    ]

    for event in events:
        uid = f'skola-event-{event.pk}@local'
        dtstart = event.start_date.strftime('%Y%m%d')
        dtend = (event.end_date + timedelta(days=1)).strftime('%Y%m%d')
        summary = (event.title or '').replace('\n', ' ').replace(',', '\\,').replace(';', '\\;')
        description = (event.description or '').replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')
        location = (event.location or '').replace('\n', ' ').replace(',', '\\,').replace(';', '\\;')

        lines.extend(
            [
                'BEGIN:VEVENT',
                f'UID:{uid}',
                f'DTSTART;VALUE=DATE:{dtstart}',
                f'DTEND;VALUE=DATE:{dtend}',
                f'SUMMARY:{summary}',
                f'DESCRIPTION:{description}',
                f'LOCATION:{location}',
                'END:VEVENT',
            ]
        )

    lines.append('END:VCALENDAR')
    payload = '\r\n'.join(lines) + '\r\n'

    response = HttpResponse(payload, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = 'inline; filename="skola-events.ics"'
    return response
