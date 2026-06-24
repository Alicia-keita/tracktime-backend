def is_admin_or_rh(user):
    role = (getattr(user, 'role', None) or '').lower()
    return role in ('admin', 'rh')
