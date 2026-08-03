import csv
from datetime import date

from django.db.models import Count, IntegerField, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponse
from django.shortcuts import render

from attendance.models import Attendance
from departments.models import Department
from employees.models import Employee
from leave_management.models import LeaveRequest
from payroll.models import Payroll


MONTHS = list(Payroll.MONTH_CHOICES)


def _filter_context(request):
    """Build shared filter choices and retain selected query values."""
    years = set(Payroll.objects.values_list('year', flat=True))
    years.update(Attendance.objects.values_list('date__year', flat=True))
    years.update(LeaveRequest.objects.values_list('start_date__year', flat=True))
    years.update(Employee.objects.values_list('date_of_joining__year', flat=True))
    return {
        'employees': Employee.objects.order_by('first_name', 'last_name'),
        'departments': Department.objects.filter(status='Active').order_by('department_name'),
        'months': MONTHS,
        'years': sorted(year for year in years if year),
        'selected': {
            'search': request.GET.get('search', '').strip(),
            'employee': request.GET.get('employee', ''),
            'department': request.GET.get('department', ''),
            'month': request.GET.get('month', ''),
            'year': request.GET.get('year', ''),
        },
    }


def _common_employee_filters(queryset, request, employee_relation=False):
    selected = _filter_context(request)['selected']
    relation = 'employee__' if employee_relation else ''
    if selected['employee']:
        queryset = queryset.filter(**{f'{relation}id': selected['employee']})
    if selected['department']:
        queryset = queryset.filter(**{f'{relation}department': selected['department']})
    if selected['search']:
        search = selected['search']
        queryset = queryset.filter(
            Q(**{f'{relation}employee_id__icontains': search})
            | Q(**{f'{relation}first_name__icontains': search})
            | Q(**{f'{relation}last_name__icontains': search})
            | Q(**{f'{relation}email__icontains': search})
        )
    return queryset


def reports_dashboard(request):
    today = date.today()
    context = {
        'employee_count': Employee.objects.filter(is_active=True).count(),
        'attendance_count': Attendance.objects.filter(date=today).count(),
        'pending_leave_count': LeaveRequest.objects.filter(status='Pending').count(),
        'payroll_total': Payroll.objects.filter(status='Paid').aggregate(total=Sum('net_salary'))['total'] or 0,
        'department_count': Department.objects.filter(status='Active').count(),
    }
    return render(request, 'reports/dashboard.html', context)


def employee_report(request):
    employees = _common_employee_filters(Employee.objects.all(), request).order_by('employee_id')
    context = _filter_context(request)
    context.update({'report_title': 'Employee Report', 'report_key': 'employees', 'records': employees})
    return render(request, 'reports/employee_report.html', context)


def attendance_report(request):
    records = _common_employee_filters(Attendance.objects.select_related('employee'), request, employee_relation=True)
    selected = _filter_context(request)['selected']
    if selected['month']:
        records = records.filter(date__month=_month_number(selected['month']))
    if selected['year'].isdigit():
        records = records.filter(date__year=int(selected['year']))
    context = _filter_context(request)
    context.update({'report_title': 'Attendance Report', 'report_key': 'attendance', 'records': records.order_by('-date', 'employee__employee_id')})
    return render(request, 'reports/attendance_report.html', context)


def leave_report(request):
    records = _common_employee_filters(LeaveRequest.objects.select_related('employee'), request, employee_relation=True)
    selected = _filter_context(request)['selected']
    if selected['month']:
        records = records.filter(start_date__month=_month_number(selected['month']))
    if selected['year'].isdigit():
        records = records.filter(start_date__year=int(selected['year']))
    context = _filter_context(request)
    context.update({'report_title': 'Leave Report', 'report_key': 'leave', 'records': records.order_by('-start_date', 'employee__employee_id')})
    return render(request, 'reports/leave_report.html', context)


def payroll_report(request):
    records = _common_employee_filters(Payroll.objects.select_related('employee'), request, employee_relation=True)
    selected = _filter_context(request)['selected']
    if selected['month']:
        records = records.filter(month=selected['month'])
    if selected['year'].isdigit():
        records = records.filter(year=int(selected['year']))
    context = _filter_context(request)
    context.update({'report_title': 'Payroll Report', 'report_key': 'payroll', 'records': records.order_by('-year', '-created_at')})
    return render(request, 'reports/payroll_report.html', context)


def department_report(request):
    selected = _filter_context(request)['selected']
    departments = Department.objects.all()
    if selected['department']:
        departments = departments.filter(department_name=selected['department'])
    if selected['search']:
        departments = departments.filter(
            Q(department_name__icontains=selected['search'])
            | Q(department_code__icontains=selected['search'])
            | Q(department_head__icontains=selected['search'])
        )
    employee_counts = Employee.objects.filter(department=OuterRef('department_name')).values('department').annotate(total=Count('pk')).values('total')
    records = departments.annotate(employee_total=Coalesce(Subquery(employee_counts, output_field=IntegerField()), 0)).order_by('department_name')
    context = _filter_context(request)
    context.update({'report_title': 'Department Report', 'report_key': 'departments', 'records': records})
    return render(request, 'reports/department_report.html', context)


def _month_number(month_name):
    return next((index for index, (_, label) in enumerate(MONTHS, start=1) if label == month_name), 0)


def export_excel(request, report_type):
    """Export the current report/filter selection as UTF-8 CSV, readable by Excel."""
    report_data = {
        'employees': ('employee_report', ['Employee ID', 'Name', 'Email', 'Department', 'Designation', 'Joining Date', 'Status']),
        'attendance': ('attendance_report', ['Employee ID', 'Employee', 'Date', 'Department', 'Status', 'Check In', 'Check Out']),
        'leave': ('leave_report', ['Employee ID', 'Employee', 'Leave Type', 'Start Date', 'End Date', 'Status']),
        'payroll': ('payroll_report', ['Employee ID', 'Employee', 'Month', 'Year', 'Basic Salary', 'Allowances', 'Deductions', 'Net Salary', 'Status']),
        'departments': ('department_report', ['Department', 'Code', 'Head', 'Employees', 'Status']),
    }
    if report_type not in report_data:
        raise Http404('Unknown report type.')

    view_name, headers = report_data[report_type]
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(headers)
    context = {'request': request}
    # Reuse each report's query logic without rendering a separate data layer.
    if view_name == 'employee_report':
        rows = _common_employee_filters(Employee.objects.all(), request).order_by('employee_id')
        for item in rows: writer.writerow([item.employee_id, f'{item.first_name} {item.last_name}', item.email, item.department, item.designation, item.date_of_joining, 'Active' if item.is_active else 'Inactive'])
    elif view_name == 'attendance_report':
        rows = _common_employee_filters(Attendance.objects.select_related('employee'), request, employee_relation=True); selected = _filter_context(request)['selected']
        if selected['month']: rows = rows.filter(date__month=_month_number(selected['month']))
        if selected['year'].isdigit(): rows = rows.filter(date__year=int(selected['year']))
        for item in rows.order_by('-date'): writer.writerow([item.employee.employee_id, str(item.employee), item.date, item.employee.department, item.status, item.check_in_time or '', item.check_out_time or ''])
    elif view_name == 'leave_report':
        rows = _common_employee_filters(LeaveRequest.objects.select_related('employee'), request, employee_relation=True); selected = _filter_context(request)['selected']
        if selected['month']: rows = rows.filter(start_date__month=_month_number(selected['month']))
        if selected['year'].isdigit(): rows = rows.filter(start_date__year=int(selected['year']))
        for item in rows.order_by('-start_date'): writer.writerow([item.employee.employee_id, str(item.employee), item.leave_type, item.start_date, item.end_date, item.status])
    elif view_name == 'payroll_report':
        rows = _common_employee_filters(Payroll.objects.select_related('employee'), request, employee_relation=True); selected = _filter_context(request)['selected']
        if selected['month']: rows = rows.filter(month=selected['month'])
        if selected['year'].isdigit(): rows = rows.filter(year=int(selected['year']))
        for item in rows.order_by('-year', '-created_at'): writer.writerow([item.employee.employee_id, str(item.employee), item.month, item.year, item.basic_salary, item.allowances, item.deductions, item.net_salary, item.status])
    else:
        employee_counts = Employee.objects.filter(department=OuterRef('department_name')).values('department').annotate(total=Count('pk')).values('total')
        rows = Department.objects.annotate(employee_total=Coalesce(Subquery(employee_counts, output_field=IntegerField()), 0))
        selected = _filter_context(request)['selected']
        if selected['department']: rows = rows.filter(department_name=selected['department'])
        if selected['search']: rows = rows.filter(Q(department_name__icontains=selected['search']) | Q(department_code__icontains=selected['search']) | Q(department_head__icontains=selected['search']))
        for item in rows.order_by('department_name'): writer.writerow([item.department_name, item.department_code, item.department_head or '', item.employee_total, item.status])
    return response
