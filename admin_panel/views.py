from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from datetime import date

from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leave_management.models import LeaveRequest


@user_passes_test(lambda user: user.is_staff, login_url='login')
def admin_dashboard(request):

    employee_count = Employee.objects.count()
    department_count = Department.objects.count()

    # Count today's attendance
    attendance_count = Attendance.objects.filter(date=date.today()).count()

    # Count pending leave requests
    leave_requests_count = LeaveRequest.objects.filter(status='Pending').count()

    context = {
        'employee_count': employee_count,
        'department_count': department_count,
        'attendance_count': attendance_count,
        'leave_requests_count': leave_requests_count,
    }

    return render(
        request,
        'admin_panel/admin_dashboard.html',
        context
    )
