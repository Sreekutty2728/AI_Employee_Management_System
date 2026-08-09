from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LeaveRequest
from .forms import LeaveRequestForm


def leave_list(request):
    leave_requests = LeaveRequest.objects.all().order_by(
        '-applied_on'
    )

    return render(
        request,
        'leave_management/leave_list.html',
        {
            'leave_requests': leave_requests,
            'is_admin': request.user.is_authenticated and request.user.is_staff,
        }
    )


def add_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('leave_list')

    else:
        form = LeaveRequestForm()

    return render(
        request,
        'leave_management/add_leave.html',
        {'form': form}
    )


def edit_leave(request, id):
    leave_request = get_object_or_404(
        LeaveRequest,
        id=id
    )

    if request.method == 'POST':
        form = LeaveRequestForm(
            request.POST,
            instance=leave_request
        )

        if form.is_valid():
            form.save()
            return redirect('leave_list')

    else:
        form = LeaveRequestForm(
            instance=leave_request
        )

    return render(
        request,
        'leave_management/edit_leave.html',
        {'form': form}
    )


@login_required
@user_passes_test(lambda user: user.is_staff)
def approve_leave(request, id):
    leave_request = get_object_or_404(
        LeaveRequest,
        id=id
    )

    if request.method == 'POST':
        leave_request.status = 'Approved'
        leave_request.save()

    return redirect('leave_list')


@login_required
@user_passes_test(lambda user: user.is_staff)
def reject_leave(request, id):
    leave_request = get_object_or_404(
        LeaveRequest,
        id=id
    )

    if request.method == 'POST':
        leave_request.status = 'Rejected'
        leave_request.save()

    return redirect('leave_list')


def delete_leave(request, id):
    leave_request = get_object_or_404(
        LeaveRequest,
        id=id
    )

    if request.method == 'POST':
        leave_request.delete()
        return redirect('leave_list')

    return render(
        request,
        'leave_management/delete_leave.html',
        {'leave_request': leave_request}
    )
