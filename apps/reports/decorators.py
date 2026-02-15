from django.shortcuts import redirect
from django.utils import timezone
from functools import wraps


def sudo_required(view_func):
    """
    Decorator that checks if the user has verified their password recently (sudo mode).
    If not, redirects to the password verification page or reports hub.
    Sudo mode lasts for 5 minutes (300 seconds).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        last_verified = request.session.get('last_password_verified_at')
        if last_verified:
            # Convert timestamp to datetime and check if still valid
            verified_time = timezone.datetime.fromtimestamp(
                last_verified, tz=timezone.get_current_timezone())
            time_diff = (timezone.now() - verified_time).total_seconds()

            if time_diff <= 300:  # 5 minutes = 300 seconds
                return view_func(request, *args, **kwargs)

        # Verification expired or not found
        # If we are in the hub, we redirect to verify-password
        if request.path == '/reports/' or request.path.endswith('/reports/'):
            return redirect(
                f'/administration/verify-password/?next={request.path}')

        # For specific reports, redirect to reports hub (which will then redirect to verify)
        # or we could redirect directly to verify. The original code redirected
        # to '/reports/'.
        return redirect('/reports/')

    return _wrapped_view
