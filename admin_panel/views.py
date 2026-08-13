from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from datetime import date, time
from django.utils import timezone

from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leave_management.models import LeaveRequest
from payroll.models import Payroll


@user_passes_test(lambda user: user.is_staff, login_url='login')
def admin_dashboard(request):

    employee_count = Employee.objects.count()
    department_count = Department.objects.count()
    attendance_count = Attendance.objects.filter(date=date.today()).count()
    leave_requests_count = LeaveRequest.objects.filter(status='Pending').count()

    activities = []

    for leave in LeaveRequest.objects.select_related('employee').order_by('-updated_at')[:5]:
        if leave.status == 'Pending':
            action_text = f"Requested {leave.leave_type}"
        else:
            action_text = f"{leave.leave_type} {leave.status.lower()}"

        activities.append({
            'employee': f"{leave.employee.first_name} {leave.employee.last_name}",
            'action': action_text,
            'timestamp': leave.updated_at,
        })

    for att in Attendance.objects.select_related('employee').order_by('-updated_at')[:5]:
        activities.append({
            'employee': f"{att.employee.first_name} {att.employee.last_name}",
            'action': f"Attendance marked: {att.status}",
            'timestamp': att.updated_at,
        })

    for emp in Employee.objects.order_by('-date_of_joining')[:5]:
        naive_dt = timezone.datetime.combine(emp.date_of_joining, time.min)
        aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())

        activities.append({
            'employee': f"{emp.first_name} {emp.last_name}",
            'action': "Joined as new employee",
            'timestamp': aware_dt,
        })

    for pay in Payroll.objects.select_related('employee').order_by('-created_at')[:5]:
        activities.append({
            'employee': f"{pay.employee.first_name} {pay.employee.last_name}",
            'action': f"Payroll processed for {pay.month} {pay.year}",
            'timestamp': pay.created_at,
        })

    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = activities[:10]

    context = {
        'employee_count': employee_count,
        'department_count': department_count,
        'attendance_count': attendance_count,
        'leave_requests_count': leave_requests_count,
        'recent_activities': recent_activities,
    }

    return render(
        request,
        'admin_panel/admin_dashboard.html',
        context
    )