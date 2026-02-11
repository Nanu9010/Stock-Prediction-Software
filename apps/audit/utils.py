"""
Audit logging utilities
"""
from apps.audit.models import AuditLog


def log_action(user, action, entity_type, entity_id, old_values=None, new_values=None, notes=None):
    """
    Log an action to the audit trail
    
    Args:
        user: User performing the action
        action: Action type (e.g., 'CREATE', 'UPDATE', 'DELETE')
        entity_type: Type of entity (e.g., 'ResearchCall', 'Portfolio')
        entity_id: ID of the entity
        old_values: Previous values (for updates)
        new_values: New values
        notes: Additional notes
    
    Returns:
        AuditLog: Created audit log entry
    """
    return AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values or {},
        new_values=new_values or {},
        notes=notes or ''
    )


def get_entity_history(entity_type, entity_id, limit=50):
    """
    Get audit history for a specific entity
    
    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
        limit: Maximum number of records to return
    
    Returns:
        QuerySet: Audit log entries
    """
    return AuditLog.objects.filter(
        entity_type=entity_type,
        entity_id=entity_id
    ).select_related('user').order_by('-timestamp')[:limit]


def get_user_activity(user, limit=100):
    """
    Get recent activity for a user
    
    Args:
        user: User instance
        limit: Maximum number of records to return
    
    Returns:
        QuerySet: Audit log entries
    """
    return AuditLog.objects.filter(
        user=user
    ).order_by('-timestamp')[:limit]
