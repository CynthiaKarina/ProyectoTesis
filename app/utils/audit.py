from app import db


def log_user_action(user_id: int | None, action: str, from_value: str | None = None, to_value: str | None = None, extra: str | None = None):
    """Registra una acción del usuario en AuditLog de forma resiliente."""
    try:
        from app.models.audit_log import AuditLog
        audit = AuditLog(
            action=action[:100] if action else 'accion',
            actor_id=user_id,
            target_user_id=user_id,
            from_value=(from_value or '')[:255] or None,
            to_value=(to_value or '')[:255] or None,
            extra=extra
        )
        db.session.add(audit)
        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        # No propagar; logging silencioso
        return False
    return True


