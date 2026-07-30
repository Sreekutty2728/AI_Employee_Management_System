from django.shortcuts import render
from employees.models import Employee
from departments.models import Department


def admin_dashboard(request):

    employee_count = Employee.objects.count()
    department_count = Department.objects.count()

    context = {
        'employee_count': employee_count,
        'department_count': department_count,
    }

    return render(
        request,
        'admin_panel/admin_dashboard.html',
        context
    )