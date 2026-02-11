"""
Research call services - Business logic for research call operations
"""
from django.db import transaction
from django.utils import timezone
from apps.research_calls.models import ResearchCall, ResearchCallEvent, ResearchCallVersion
from apps.audit.models import AuditLog


@transaction.atomic
def create_research_call(data, created_by):
    """
    Create a new research call with validation and event logging
    
    Args:
        data: Dictionary of call data
        created_by: User creating the call
    
    Returns:
        ResearchCall: Created call instance
    """
    call = ResearchCall.objects.create(
        created_by=created_by,
        **data
    )
    
    # Create initial event
    ResearchCallEvent.objects.create(
        research_call=call,
        event_type='CREATED',
        triggered_by=created_by,
        notes=f'Call created by {created_by.get_full_name()}'
    )
    
    # Create initial version
    ResearchCallVersion.objects.create(
        research_call=call,
        version_number=1,
        changed_by=created_by,
        change_summary='Initial version'
    )
    
    # Audit log
    AuditLog.objects.create(
        user=created_by,
        action='CREATE_RESEARCH_CALL',
        entity_type='ResearchCall',
        entity_id=call.id,
        new_values={'symbol': call.symbol, 'action': call.action}
    )
    
    return call


@transaction.atomic
def approve_research_call(call, approved_by):
    """
    Approve a research call
    
    Args:
        call: ResearchCall instance
        approved_by: User approving the call
    
    Returns:
        ResearchCall: Updated call
    """
    if call.status != 'PENDING_APPROVAL':
        raise ValueError('Only pending calls can be approved')
    
    call.status = 'APPROVED'
    call.approved_by = approved_by
    call.approved_at = timezone.now()
    call.save()
    
    # Create event
    ResearchCallEvent.objects.create(
        research_call=call,
        event_type='APPROVED',
        triggered_by=approved_by,
        notes=f'Call approved by {approved_by.get_full_name()}'
    )
    
    # Audit log
    AuditLog.objects.create(
        user=approved_by,
        action='APPROVE_RESEARCH_CALL',
        entity_type='ResearchCall',
        entity_id=call.id
    )
    
    return call


@transaction.atomic
def publish_research_call(call, published_by):
    """
    Publish an approved research call
    
    Args:
        call: ResearchCall instance
        published_by: User publishing the call
    
    Returns:
        ResearchCall: Updated call
    """
    if call.status != 'APPROVED':
        raise ValueError('Only approved calls can be published')
    
    call.status = 'ACTIVE'
    call.published_at = timezone.now()
    call.save()
    
    # Create event
    ResearchCallEvent.objects.create(
        research_call=call,
        event_type='PUBLISHED',
        triggered_by=published_by,
        notes=f'Call published by {published_by.get_full_name()}'
    )
    
    # Audit log
    AuditLog.objects.create(
        user=published_by,
        action='PUBLISH_RESEARCH_CALL',
        entity_type='ResearchCall',
        entity_id=call.id
    )
    
    # Future: Send notifications to subscribers
    
    return call


@transaction.atomic
def close_research_call(call, reason, closed_by):
    """
    Close a research call
    
    Args:
        call: ResearchCall instance
        reason: Reason for closing
        closed_by: User closing the call
    
    Returns:
        ResearchCall: Updated call
    """
    call.status = 'CLOSED'
    call.closed_at = timezone.now()
    call.save()
    
    # Create event
    ResearchCallEvent.objects.create(
        research_call=call,
        event_type='CLOSED',
        triggered_by=closed_by,
        notes=f'Call closed: {reason}'
    )
    
    # Audit log
    AuditLog.objects.create(
        user=closed_by,
        action='CLOSE_RESEARCH_CALL',
        entity_type='ResearchCall',
        entity_id=call.id,
        new_values={'reason': reason}
    )
    
    return call
