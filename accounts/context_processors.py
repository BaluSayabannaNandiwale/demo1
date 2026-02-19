"""
Context processor to expose a session-like object for templates.
Templates from the Flask conversion expect session.name, session.email, session.logged_in, session.user_role.
"""
def session_context(request):
    """Provide session-like context for template compatibility."""
    if request.user.is_authenticated:
        return {
            'session': {
                'logged_in': True,
                'name': getattr(request.user, 'name', request.user.get_username()),
                'email': getattr(request.user, 'email', ''),
                'user_role': getattr(request.user, 'user_type', 'student'),
            }
        }
    return {'session': {'logged_in': False, 'name': '', 'email': '', 'user_role': ''}}
