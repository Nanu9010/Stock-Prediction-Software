"""
Broker services - Business logic for broker operations
"""
from django.db import transaction
from apps.brokers.models import Broker, BrokerPerformanceMetrics
from apps.research_calls.models import ResearchCall
from django.utils import timezone
from datetime import timedelta


def calculate_broker_accuracy(broker, days=30):
    """
    Calculate broker's accuracy over the last N days
    
    Args:
        broker: Broker instance
        days: Number of days to look back
    
    Returns:
        dict: Accuracy metrics
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    closed_calls = ResearchCall.objects.filter(
        broker=broker,
        status='CLOSED',
        closed_at__gte=cutoff_date
    )
    
    total_closed = closed_calls.count()
    if total_closed == 0:
        return {
            'total_calls': 0,
            'successful_calls': 0,
            'accuracy_percentage': 0,
            'avg_return': 0,
        }
    
    successful_calls = closed_calls.filter(is_successful=True).count()
    accuracy = (successful_calls / total_closed) * 100
    
    # Calculate average return
    returns = [call.actual_return_percentage for call in closed_calls if call.actual_return_percentage]
    avg_return = sum(returns) / len(returns) if returns else 0
    
    return {
        'total_calls': total_closed,
        'successful_calls': successful_calls,
        'accuracy_percentage': round(accuracy, 2),
        'avg_return': round(avg_return, 2),
    }


@transaction.atomic
def update_broker_metrics(broker):
    """
    Update broker's overall performance metrics
    
    Args:
        broker: Broker instance
    """
    metrics = calculate_broker_accuracy(broker, days=365)  # Last year
    
    broker.overall_accuracy = metrics['accuracy_percentage']
    broker.total_calls_published = ResearchCall.objects.filter(
        broker=broker,
        status__in=['ACTIVE', 'CLOSED']
    ).count()
    broker.save(update_fields=['overall_accuracy', 'total_calls_published', 'updated_at'])
    
    return broker


def get_top_brokers(limit=10):
    """
    Get top performing brokers by accuracy
    
    Args:
        limit: Number of brokers to return
    
    Returns:
        QuerySet: Top brokers
    """
    return Broker.objects.filter(
        is_active=True,
        is_verified=True,
        total_calls_published__gte=10  # Minimum 10 calls
    ).order_by('-overall_accuracy')[:limit]
