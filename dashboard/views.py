from django.shortcuts import render
from django.db.models import Count, Sum, Q, Max, Avg, F, ExpressionWrapper, FloatField, Case, When
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
import json

from events.models import Event
from clients.models import Client
from people.models import Person

def dashboard(request):
    # Get current date and calculate 12 months ago date
    today = timezone.now().date()
    year_start = today.replace(month=1, day=1)
    twelve_months_ago = today - timedelta(days=365)
    
    # Events data for the current year
    events_this_year = Event.objects.filter(start_datetime__date__gte=year_start)
    total_events_count = events_this_year.count()
    total_events_value = events_this_year.aggregate(Sum('value'))['value__sum'] or 0
    
    # Count total people and clients
    total_people_count = Person.objects.count()
    total_clients_count = Client.objects.count()
    
    # Count active and dormant clients
    # Active clients: with events in the last 12 months
    active_clients = Client.objects.filter(
        events__start_datetime__date__gte=twelve_months_ago
    ).distinct().count()
    
    # Dormant clients: with events, but none in the last 12 months
    dormant_clients = Client.objects.filter(
        events__isnull=False
    ).exclude(
        events__start_datetime__date__gte=twelve_months_ago
    ).distinct().count()
    
    # Get top rated people (based on average of all rating fields)
    # First, create a queryset that calculates the average rating for each person
    top_rated_people = Person.objects.filter(
        # Ensure at least one rating field is not null
        Q(efficiency__isnull=False) | 
        Q(punctuality__isnull=False) | 
        Q(proactivity__isnull=False) | 
        Q(appearance__isnull=False) | 
        Q(communication__isnull=False)
    ).annotate(
        # Calculate the average rating diretamente
        avg_rating=ExpressionWrapper(
            (
                Coalesce(F('efficiency'), 0) + 
                Coalesce(F('punctuality'), 0) + 
                Coalesce(F('proactivity'), 0) + 
                Coalesce(F('appearance'), 0) + 
                Coalesce(F('communication'), 0)
            ) / 
            (
                Case(
                    When(efficiency__isnull=False, then=1),
                    default=0
                ) +
                Case(
                    When(punctuality__isnull=False, then=1),
                    default=0
                ) +
                Case(
                    When(proactivity__isnull=False, then=1),
                    default=0
                ) +
                Case(
                    When(appearance__isnull=False, then=1),
                    default=0
                ) +
                Case(
                    When(communication__isnull=False, then=1),
                    default=0
                )
            ),
            output_field=FloatField()
        )
    ).order_by('-avg_rating')[:5]  # Get top 5 rated people
    
    # Events data for the last 12 months (monthly breakdown)
    monthly_data = {}
    for i in range(12):
        month = (today.month - i - 1) % 12 + 1
        year = today.year if month <= today.month else today.year - 1
        month_name = timezone.datetime(year, month, 1).strftime('%b')
        
        start_date = timezone.datetime(year, month, 1).date()
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1).date()
        else:
            end_date = timezone.datetime(year, month + 1, 1).date()
        
        events = Event.objects.filter(start_datetime__date__gte=start_date, start_datetime__date__lt=end_date)
        monthly_data[month_name] = {
            'count': events.count(),
            'value': float(events.aggregate(Sum('value'))['value__sum'] or 0)
        }
    
    # Reverse the data to show in chronological order
    months_labels = list(monthly_data.keys())
    months_labels.reverse()
    counts_data = [monthly_data[month]['count'] for month in months_labels]
    values_data = [monthly_data[month]['value'] for month in months_labels]
    
    # Get top clients by number of events
    top_clients_by_events = Client.objects.filter(
        events__start_datetime__date__gte=twelve_months_ago
    ).annotate(
        event_count=Count('events')
    ).order_by('-event_count')[:5]
    
    # Get top clients by total value
    top_clients_by_value = Client.objects.filter(
        events__start_datetime__date__gte=twelve_months_ago
    ).annotate(
        total_value=Sum('events__value')
    ).order_by('-total_value')[:5]
    
    context = {
        'total_events_count': total_events_count,
        'total_events_value': total_events_value,
        'total_people_count': total_people_count,
        'total_clients_count': total_clients_count,
        'active_clients': active_clients,
        'dormant_clients': dormant_clients,
        'top_rated_people': top_rated_people,
        'months_labels_json': json.dumps(months_labels),
        'counts_data_json': json.dumps(counts_data),
        'values_data_json': json.dumps(values_data),
        'top_clients_by_events': top_clients_by_events,
        'top_clients_by_value': top_clients_by_value,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
