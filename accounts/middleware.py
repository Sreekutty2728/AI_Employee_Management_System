from django.shortcuts import redirect
from django.urls import Resolver404, resolve


class EmployeePortalMiddleware:
    """Limit authenticated employees to their own portal routes."""

    employee_allowed_routes = {
    'dashboard',
    'change_password',
    'logout',
    'login',
    'employee_login',
}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and not user.is_staff:
            try:
                match = resolve(request.path_info)
            except Resolver404:
                match = None
            if match and match.url_name not in self.employee_allowed_routes:
                return redirect('dashboard')
        return self.get_response(request)
