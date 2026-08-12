from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Department
from .forms import DepartmentForm


# ==========================
# Department List
# ==========================
def department_list(request):

    search_query = request.GET.get('search', '').strip()

    departments = Department.objects.all().order_by('department_name')

    if search_query:
        departments = departments.filter(
            Q(department_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'departments': departments,
        'search_query': search_query,
    }

    return render(
        request,
        'departments/department_list.html',
        context
    )


# ==========================
# Add Department
# ==========================
def add_department(request):

    if request.method == "POST":

        form = DepartmentForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('department_list')

    else:

        form = DepartmentForm()

    context = {
        'form': form
    }

    return render(
        request,
        'departments/add_department.html',
        context
    )


# ==========================
# Edit Department
# ==========================
def edit_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    if request.method == "POST":

        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():

            form.save()

            return redirect('department_list')

    else:

        form = DepartmentForm(
            instance=department
        )

    context = {
        'form': form,
        'department': department
    }

    return render(
        request,
        'departments/edit_department.html',
        context
    )


# ==========================
# Delete Department
# ==========================
def delete_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    if request.method == "POST":

        department.delete()

        return redirect('department_list')

    context = {
        'department': department
    }

    return render(
        request,
        'departments/delete_department.html',
        context
    )