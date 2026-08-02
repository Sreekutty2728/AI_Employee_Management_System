from django.shortcuts import render, redirect, get_object_or_404
from .models import Payroll
from .forms import PayrollForm


def payroll_list(request):
    payroll_records = Payroll.objects.all().order_by(
        '-year',
        '-created_at'
    )

    return render(
        request,
        'payroll/payroll_list.html',
        {'payroll_records': payroll_records}
    )


def add_payroll(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('payroll_list')

    else:
        form = PayrollForm()

    return render(
        request,
        'payroll/add_payroll.html',
        {'form': form}
    )


def edit_payroll(request, id):
    payroll = get_object_or_404(
        Payroll,
        id=id
    )

    if request.method == 'POST':
        form = PayrollForm(
            request.POST,
            instance=payroll
        )

        if form.is_valid():
            form.save()
            return redirect('payroll_list')

    else:
        form = PayrollForm(
            instance=payroll
        )

    return render(
        request,
        'payroll/edit_payroll.html',
        {'form': form}
    )


def delete_payroll(request, id):
    payroll = get_object_or_404(
        Payroll,
        id=id
    )

    if request.method == 'POST':
        payroll.delete()
        return redirect('payroll_list')

    return render(
        request,
        'payroll/delete_payroll.html',
        {'payroll': payroll}
    )
