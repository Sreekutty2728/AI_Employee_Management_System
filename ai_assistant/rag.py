import os
from pathlib import Path

from leave_management.models import LeaveRequest

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder containing RAG documents
KNOWLEDGE_BASE_DIR = BASE_DIR / "rag_documents"


def load_documents():
    """
    Read all text documents from the rag_documents folder
    and return their combined content.
    """
    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        return ""

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):
        try:
            content = file_path.read_text(encoding="utf-8")

            documents.append(
                f"Document: {file_path.name}\n"
                f"{content}"
            )

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return "\n\n".join(documents)


def get_leave_policy():
    """
    Load the leave policy document.
    """
    leave_policy_path = KNOWLEDGE_BASE_DIR / "leave_policy.txt"

    if not leave_policy_path.exists():
        return ""

    try:
        return leave_policy_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading leave policy: {e}")
        return ""


def get_leave_requests():
    """
    Get leave request information from the database.
    """
    leave_requests = LeaveRequest.objects.select_related("employee").all()

    if not leave_requests:
        return ""

    results = []

    for leave in leave_requests:
        results.append(
            f"Employee: {leave.employee.first_name} {leave.employee.last_name}\n"
            f"Employee ID: {leave.employee.employee_id}\n"
            f"Leave Type: {leave.leave_type}\n"
            f"Start Date: {leave.start_date}\n"
            f"End Date: {leave.end_date}\n"
            f"Reason: {leave.reason}\n"
            f"Status: {leave.status}\n"
            f"Applied On: {leave.applied_on}\n"
        )

    return "\n".join(results)


def retrieve_relevant_content(query, employee=None):
    """
    Retrieve relevant information from the leave policy
    and leave requests database.
    """

    policy = get_leave_policy()
    query_lower = query.lower()

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
        "pending leave",
        "rejected leave",
        "how many leaves",
        "how many leave",
    ]

    if any(keyword in query_lower for keyword in leave_request_keywords):

        if employee:
            all_leave_requests = LeaveRequest.objects.select_related(
                "employee"
            ).filter(employee=employee)
        else:
            all_leave_requests = LeaveRequest.objects.select_related(
                "employee"
            ).all()

        filtered_requests = []

        # STEP 3 FIX:
        # The records are already filtered for the logged-in employee,
        # so we don't check the employee name in the question anymore.
        for leave in all_leave_requests:
            filtered_requests.append(
                f"Employee: {leave.employee.first_name} {leave.employee.last_name}\n"
                f"Employee ID: {leave.employee.employee_id}\n"
                f"Leave Type: {leave.leave_type}\n"
                f"Start Date: {leave.start_date}\n"
                f"End Date: {leave.end_date}\n"
                f"Reason: {leave.reason}\n"
                f"Status: {leave.status}\n"
                f"Applied On: {leave.applied_on}\n"
            )

        leave_requests = "\n".join(filtered_requests)

        return (
            "EMPLOYEE LEAVE POLICY\n\n"
            + policy
            + "\n\n"
            + "LEAVE REQUESTS FROM DATABASE\n\n"
            + leave_requests
        )

    if not policy:
        return ""

    query_words = set(query_lower.split())

    sections = policy.split("\n\n")
    relevant_sections = []

    for section in sections:
        section_words = set(section.lower().split())

        if query_words.intersection(section_words):
            relevant_sections.append(section)

    return "\n\n".join(relevant_sections)