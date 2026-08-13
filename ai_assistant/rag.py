from pathlib import Path

from leave_management.models import LeaveRequest


# ==================================================
# PROJECT ROOT DIRECTORY
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==================================================
# RAG DOCUMENTS FOLDER
# ==================================================

KNOWLEDGE_BASE_DIR = BASE_DIR / "rag_documents"


# ==================================================
# LOAD ALL DOCUMENTS
# ==================================================

def load_documents():
    """
    Read all .txt documents from the rag_documents folder
    and return their combined content.
    """

    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        return ""

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )

            documents.append(
                f"Document: {file_path.name}\n"
                f"{content}"
            )

        except Exception as e:
            print(
                f"Error reading {file_path}: {e}"
            )

    return "\n\n".join(documents)


# ==================================================
# LEAVE POLICY
# ==================================================

def get_leave_policy():
    """
    Load the leave policy document.
    """

    leave_policy_path = (
        KNOWLEDGE_BASE_DIR / "leave_policy.txt"
    )

    if not leave_policy_path.exists():
        return ""

    try:
        return leave_policy_path.read_text(
            encoding="utf-8"
        )

    except Exception as e:
        print(
            f"Error reading leave policy: {e}"
        )
        return ""


# ==================================================
# ATTENDANCE POLICY
# ==================================================

def get_attendance_policy():
    """
    Load the attendance policy document.
    """

    attendance_policy_path = (
        KNOWLEDGE_BASE_DIR / "attendance_policy.txt"
    )

    if not attendance_policy_path.exists():
        return ""

    try:
        return attendance_policy_path.read_text(
            encoding="utf-8"
        )

    except Exception as e:
        print(
            f"Error reading attendance policy: {e}"
        )
        return ""


# ==================================================
# WORK FROM HOME POLICY
# ==================================================

def get_work_from_home_policy():
    """
    Load the work from home policy document.
    """

    work_from_home_policy_path = (
        KNOWLEDGE_BASE_DIR
        / "work_from_home_policy.txt"
    )

    if not work_from_home_policy_path.exists():
        return ""

    try:
        return work_from_home_policy_path.read_text(
            encoding="utf-8"
        )

    except Exception as e:
        print(
            f"Error reading work from home policy: {e}"
        )
        return ""


# ==================================================
# GET EMPLOYEE LEAVE REQUESTS
# ==================================================

def get_leave_requests(employee=None):
    """
    Get leave request information from the database.

    If an employee is provided, only that employee's
    leave requests are returned.
    """

    if employee:

        leave_requests = (
            LeaveRequest.objects
            .select_related("employee")
            .filter(employee=employee)
        )

    else:

        leave_requests = (
            LeaveRequest.objects
            .select_related("employee")
            .all()
        )

    if not leave_requests.exists():
        return ""

    results = []

    for leave in leave_requests:

        results.append(
            f"Employee: "
            f"{leave.employee.first_name} "
            f"{leave.employee.last_name}\n"
            f"Employee ID: "
            f"{leave.employee.employee_id}\n"
            f"Leave Type: "
            f"{leave.leave_type}\n"
            f"Start Date: "
            f"{leave.start_date}\n"
            f"End Date: "
            f"{leave.end_date}\n"
            f"Reason: "
            f"{leave.reason}\n"
            f"Status: "
            f"{leave.status}\n"
            f"Applied On: "
            f"{leave.applied_on}\n"
        )

    return "\n".join(results)


# ==================================================
# CALCULATE APPROVED LEAVE DAYS
# ==================================================

def get_leave_days_used(employee=None):
    """
    Calculate the total number of approved leave days.

    Both start_date and end_date are included.

    Example:
        July 15 -> July 16 = 2 days

    Rejected and pending leaves are not counted.
    """

    if not employee:
        return 0

    leave_requests = (
        LeaveRequest.objects
        .filter(
            employee=employee,
            status="Approved"
        )
    )

    total_days = 0

    for leave in leave_requests:

        if leave.start_date and leave.end_date:

            days = (
                leave.end_date - leave.start_date
            ).days + 1

            total_days += days

    return total_days


# ==================================================
# GET LEAVE USAGE CONTEXT
# ==================================================

def get_leave_usage_context(employee):
    """
    Return employee leave usage information
    for the AI assistant.
    """

    leave_requests = get_leave_requests(employee)

    leave_days_used = get_leave_days_used(employee)

    if not leave_requests:

        return (
            "LEAVE USAGE INFORMATION\n\n"
            "No leave requests found for this employee.\n"
            "Approved Leave Days Used: 0 days"
        )

    return (
        "LEAVE USAGE INFORMATION\n\n"
        f"Approved Leave Days Used: "
        f"{leave_days_used} days\n\n"
        "EMPLOYEE LEAVE REQUESTS\n\n"
        f"{leave_requests}"
    )


# ==================================================
# RAG RETRIEVAL
# ==================================================

def retrieve_relevant_content(query, employee=None):
    """
    Retrieve relevant information from:

    1. Employee leave database
    2. Leave policy
    3. Attendance policy
    4. Work from home policy
    """

    query_lower = query.lower().strip()


    # ==================================================
    # 1. LEAVE DATABASE QUESTIONS
    # ==================================================

    leave_request_keywords = [

        "leave request",
        "leave requests",
        "my leave",
        "my leaves",
        "applied leave",
        "applied leaves",
        "leave status",
        "leave application",
        "leave applications",
        "approved leave",
        "approved leaves",
        "pending leave",
        "pending leaves",
        "rejected leave",
        "rejected leaves",
        "how many leaves",
        "how many leave",
        "leave have i taken",
        "leaves have i taken",
        "how many sick leaves",
        "sick leaves have i taken",
        "leave used",
        "leaves used",
        "how many days of leave",
        "how many leave days",
        "leave balance",
        "remaining leave",
        "leaves left",
        "leave left",
    ]

    if any(
        keyword in query_lower
        for keyword in leave_request_keywords
    ):

        policy = get_leave_policy()

        leave_usage = get_leave_usage_context(
            employee
        )

        return (
            "EMPLOYEE LEAVE POLICY\n\n"
            + policy
            + "\n\n"
            + leave_usage
        )


    # ==================================================
    # 2. ATTENDANCE POLICY QUESTIONS
    # ==================================================

    attendance_keywords = [

        "attendance policy",
        "attendance policies",
        "attendance",
        "check in",
        "check-in",
        "check out",
        "check-out",
        "attendance record",
        "attendance records",
        "attendance status",
        "present status",
        "absent status",
        "half day",
        "half-day",
        "attendance correction",
        "attendance corrections",
        "attendance rules",
    ]

    if any(
        keyword in query_lower
        for keyword in attendance_keywords
    ):

        attendance_policy = (
            get_attendance_policy()
        )

        if attendance_policy:

            return (
                "EMPLOYEE ATTENDANCE POLICY\n\n"
                + attendance_policy
            )

        return (
            "The attendance policy is not available "
            "in the current knowledge base."
        )


    # ==================================================
    # 3. WORK FROM HOME POLICY QUESTIONS
    # ==================================================

    work_from_home_keywords = [

        "work from home",
        "work-from-home",
        "wfh",
        "remote work",
        "remote working",
        "work remotely",
        "working remotely",
        "work at home",
        "working from home",
        "wfh policy",
        "remote work policy",
    ]

    if any(
        keyword in query_lower
        for keyword in work_from_home_keywords
    ):

        work_from_home_policy = (
            get_work_from_home_policy()
        )

        if work_from_home_policy:

            return (
                "EMPLOYEE WORK FROM HOME POLICY\n\n"
                + work_from_home_policy
            )

        return (
            "The work from home policy is not "
            "available in the current knowledge base."
        )


    # ==================================================
    # 4. GENERAL LEAVE POLICY QUESTIONS
    # ==================================================

    leave_policy_keywords = [

        "leave policy",
        "leave policies",
        "sick leave",
        "casual leave",
        "annual leave",
        "leave application",
        "leave approval",
        "leave rules",
        "leave status",
    ]

    if any(
        keyword in query_lower
        for keyword in leave_policy_keywords
    ):

        policy = get_leave_policy()

        if policy:

            return (
                "EMPLOYEE LEAVE POLICY\n\n"
                + policy
            )

        return (
            "The leave policy is not available "
            "in the current knowledge base."
        )


    # ==================================================
    # 5. NO COMPANY POLICY MATCH
    # ==================================================

    return ""