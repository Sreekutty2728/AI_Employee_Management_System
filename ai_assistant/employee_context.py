from employees.models import Employee
from leave_management.models import LeaveRequest


def get_employee_context(employee):
    """
    Build a context containing information belonging
    only to the logged-in employee.
    """

    context = []

    # -----------------------------
    # EMPLOYEE INFORMATION
    # -----------------------------
    context.append(
        "EMPLOYEE INFORMATION\n"
        f"Employee ID: {employee.employee_id}\n"
        f"Name: {employee.first_name} {employee.last_name}\n"
        f"Email: {employee.email}\n"
        f"Phone: {employee.phone}\n"
        f"Date of Birth: {employee.date_of_birth}\n"
        f"Gender: {employee.gender}\n"
        f"Address: {employee.address}\n"
        f"Department: {employee.department}\n"
        f"Designation: {employee.designation}\n"
        f"Date of Joining: {employee.date_of_joining}\n"
        f"Salary: ₹{employee.salary}\n"
        f"Active: {employee.is_active}"
    )

    # -----------------------------
    # LEAVE INFORMATION
    # -----------------------------
    leave_requests = LeaveRequest.objects.filter(
        employee=employee
    ).order_by("-start_date")

    if leave_requests.exists():

        leave_data = ["EMPLOYEE LEAVE INFORMATION"]

        for leave in leave_requests:
            leave_data.append(
                f"Leave Type: {leave.leave_type}\n"
                f"Start Date: {leave.start_date}\n"
                f"End Date: {leave.end_date}\n"
                f"Reason: {leave.reason}\n"
                f"Status: {leave.status}\n"
                f"Applied On: {leave.applied_on}"
            )

        context.append("\n".join(leave_data))

    else:
        context.append(
            "EMPLOYEE LEAVE INFORMATION\n"
            "No leave requests found."
        )

    return "\n\n".join(context)