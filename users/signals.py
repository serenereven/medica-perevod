from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.dispatch import receiver


@receiver(user_logged_in)
def limit_user_sessions(sender, request, user, **kwargs):
    """Ограничение количества активных сессий у пользователя"""

    current_session_key = request.session.session_key
    max_sessions = 1

    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    user_sessions = []
    for session in sessions:
        data = session.get_decoded()
        if str(data.get("_auth_user_id")) == str(user.pk):
            if session.session_key != current_session_key:
                user_sessions.append(session)

    # Удаляем самые старые, оставляем max_sessions - 1 (+ текущая = max_sessions)
    if len(user_sessions) >= max_sessions:
        for session in user_sessions:
            session.delete()
