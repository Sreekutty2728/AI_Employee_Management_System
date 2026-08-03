from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

from attendance.models import Attendance
from employees.models import Employee
from leave_management.models import LeaveRequest
from payroll.models import Payroll


def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'dashboard')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            if hasattr(user, 'employee_profile'):
                return redirect('dashboard')

            logout(request)
            messages.error(request, 'This account is not linked to an employee profile.')
        else:
            messages.error(request, 'Invalid username or password.')


    return render(request,'accounts/login.html')



@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    employee = get_object_or_404(Employee, user=request.user)
    context = {
        'employee': employee,
        'attendance_records': Attendance.objects.filter(employee=employee).order_by('-date')[:10],
        'leave_requests': LeaveRequest.objects.filter(employee=employee).order_by('-start_date')[:10],
        'payroll_records': Payroll.objects.filter(employee=employee).order_by('-year', '-created_at')[:10],
    }
    return render(request, 'accounts/dashboard.html', context)


@require_POST
def logout_view(request):
    """End the authenticated session and return the user to the login page."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
