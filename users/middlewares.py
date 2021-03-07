from django.contrib.sessions.models import Session
from django.http import HttpRequest

def one_session_pre_user_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request: HttpRequest):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.user.is_authenticated:
            stored_session_key = request.user.logged_in_user.session_key or ''

            # if there is a stored_session_key  in our database and it is
            # different from the current session, delete the stored_session_key
            # session_key with from the Session table
            if stored_session_key and stored_session_key != request.session.session_key:
                Session.objects.get(session_key=stored_session_key).delete()

            request.user.logged_in_user.session_key = request.session.session_key
            request.user.logged_in_user.save()

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware