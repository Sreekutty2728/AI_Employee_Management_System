from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Employee
from .forms import EmployeeForm


def employee_list(request):
    search_query = request.GET.get('search', '').strip()

    employees = Employee.objects.all().order_by('employee_id')

    if search_query:
        employees = employees.filter(
            Q(employee_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

    return render(
        request,
        'employees/employee_list.html',
        {
            'employees': employees,
            'search_query': search_query,
        }
    )


def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('employee_list')
        else:
            print("FORM ERRORS:")
            print(form.errors)

    else:
        form = EmployeeForm()

    return render(request, 'employees/add_employee.html', {'form': form})

def edit_employee(request, id):
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/edit_employee.html', {'form': form})


def delete_employee(request, id):
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')

    return render(request, 'employees/delete_employee.html', {'employee': employee})

def employee_detail(request, id):
    employee = get_object_or_404(Employee, id=id)

    return render(
        request,
        'employees/employee_detail.html',
        {'employee': employee}
    )