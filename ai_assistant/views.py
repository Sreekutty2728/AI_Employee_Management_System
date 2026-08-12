from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employees.models import Employee
import markdown

from .rag import retrieve_relevant_content
from .employee_context import get_employee_context

import os
from google import genai


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =========================================================
# 1. DIRECT EMPLOYEE DATABASE ANSWERS
# =========================================================

def get_direct_employee_answer(question, employee):
    question_lower = question.lower()

    # Salary
    if "salary" in question_lower or "pay" in question_lower:
        return f"Your monthly salary is **₹{employee.salary}**."

    # Designation
    if "designation" in question_lower or "job title" in question_lower:
        return f"Your designation is **{employee.designation}**."

    # Department
    if "department" in question_lower:
        return f"Your department is **{employee.department}**."

    # Employee ID
    if (
        "employee id" in question_lower
        or "employee number" in question_lower
    ):
        return f"Your employee ID is **{employee.employee_id}**."

    # Email
    if "email" in question_lower or "email address" in question_lower:
        return f"Your email address is **{employee.email}**."

    # Phone
    if "phone" in question_lower or "phone number" in question_lower:
        return f"Your phone number is **{employee.phone}**."

    # Joining date
    if (
        "joining date" in question_lower
        or "date of joining" in question_lower
        or "when did i join" in question_lower
    ):
        return f"Your date of joining is **{employee.date_of_joining}**."

    return None


# =========================================================
# 2. DETECT COMPANY / HR / POLICY QUESTIONS
# =========================================================

def is_company_policy_question(question):
    question_lower = question.lower()

    policy_keywords = [
        "leave policy",
        "leave policies",
        "sick leave policy",
        "casual leave policy",
        "annual leave policy",
        "leave application",
        "how do i apply for leave",
        "how can i apply for leave",
        "leave approval",
        "leave rules",
        "leave request rules",
        "leave status",
        "company policy",
        "company policies",
        "attendance policy",
        "attendance rules",
        "hr policy",
        "hr policies",
    ]

    return any(
        keyword in question_lower
        for keyword in policy_keywords
    )


# =========================================================
# 3. GET DIRECT RAG ANSWER
# =========================================================

def get_direct_rag_answer(question, employee):
    """
    Get company-policy information directly from RAG.

    This avoids Gemini for questions that can be answered
    directly from the company's knowledge base.
    """

    if not is_company_policy_question(question):
        return None

    rag_content = retrieve_relevant_content(
        question,
        employee
    )

    if not rag_content:
        return (
            "The requested information is not available "
            "in the current company policy documents. "
            "Please contact the administrator."
        )

    return rag_content


# =========================================================
# 4. AI CHAT VIEW
# =========================================================

@login_required
def chat(request):

    messages = []

    # Get the currently logged-in employee
    employee = Employee.objects.get(
        user=request.user
    )

    # =====================================================
    # HANDLE POST REQUEST
    # =====================================================

    if request.method == "POST":

        question = request.POST.get(
            "question",
            ""
        ).strip()

        # -------------------------------------------------
        # Show employee question
        # -------------------------------------------------

        messages.append({
            "sender": "user",
            "text": question
        })

        # =================================================
        # TYPE 1: EMPLOYEE DATABASE QUESTION
        # =================================================

        direct_answer = get_direct_employee_answer(
            question,
            employee
        )

        if direct_answer:

            reply = markdown.markdown(
                direct_answer
            )

            messages.append({
                "sender": "ai",
                "text": reply
            })

            return render(
                request,
                "ai_assistant/chat.html",
                {
                    "messages": messages
                }
            )

        # =================================================
        # TYPE 2: COMPANY / HR / RAG QUESTION
        # =================================================

        rag_answer = get_direct_rag_answer(
            question,
            employee
        )

        if rag_answer:

            reply = markdown.markdown(
    rag_answer.replace("\n", "<br>"),
    extensions=[
        "fenced_code",
        "tables",
    ]
)

            messages.append({
                "sender": "ai",
                "text": reply
            })

            return render(
                request,
                "ai_assistant/chat.html",
                {
                    "messages": messages
                }
            )

        # =================================================
        # TYPE 3: GENERAL KNOWLEDGE → GEMINI
        # =================================================

        try:

            # -------------------------------------------------
            # Employee database context
            # -------------------------------------------------

            employee_context = get_employee_context(
                employee
            )

            # -------------------------------------------------
            # RAG context
            # -------------------------------------------------

            rag_context = retrieve_relevant_content(
                question,
                employee
            )

            # -------------------------------------------------
            # Combine contexts
            # -------------------------------------------------

            context = f"""
# EMPLOYEE DATABASE INFORMATION

{employee_context}

# COMPANY POLICY / RAG INFORMATION

{rag_context}
"""

            # -------------------------------------------------
            # Gemini prompt
            # -------------------------------------------------

            prompt = f"""
You are an AI Assistant for an Employee Management System.

Answer the employee's question accurately and naturally.

You have access to:

1. EMPLOYEE DATABASE INFORMATION
2. COMPANY POLICY / RAG INFORMATION
3. Your general knowledge for general questions.

IMPORTANT RULES:

1. EMPLOYEE-SPECIFIC QUESTIONS

If the employee asks about their own information,
use the employee database information.

Examples:

- What is my salary?
- What is my designation?
- What is my department?
- What is my employee ID?
- What is my email?
- What is my phone number?
- When did I join?

Only provide the information relevant to the question.

Do not reveal another employee's information.

2. LEAVE QUESTIONS

Use the employee's leave information from the database
when answering questions about their leave requests.

Examples:

- How many leaves have I taken?
- Show my approved leaves.
- Do I have pending leaves?
- How many sick leaves have I taken?

When calculating leave duration:

- Count both the start date and end date.
- August 12 to August 13 = 2 days.
- August 14 to August 16 = 3 days.

Do not count rejected leave as used leave.

3. LEAVE BALANCE

Only calculate remaining leave if an official leave
allowance is available.

Use:

Remaining Leave = Leave Allowance - Leave Used

Never invent a leave allowance.

4. COMPANY POLICY

Use the COMPANY POLICY / RAG INFORMATION when answering
company policy questions.

Do not invent company policies.

5. GENERAL KNOWLEDGE

For general questions such as:

- What is Python?
- What is Django?
- What is Java?
- What is machine learning?
- What is artificial intelligence?

Use your general knowledge.

6. PRIVACY

Never reveal information belonging to another employee.

Only use information belonging to the currently logged-in
employee.

7. ACCURACY

Never invent database information or company policy.

If required information is unavailable, clearly say so.

8. RESPONSE STYLE

- Answer directly.
- Keep the answer concise.
- Use bullet points when useful.
- Use headings when useful.
- Use **bold** for important information.

CONTEXT:

{context}

EMPLOYEE QUESTION:

{question}
"""

            # -------------------------------------------------
            # Call Gemini
            # -------------------------------------------------

            response = client.models.generate_content(
                model="models/gemini-3.5-flash-lite",
                contents=prompt,
            )

            # -------------------------------------------------
            # Format Gemini response
            # -------------------------------------------------

            reply = markdown.markdown(
                response.text,
                extensions=[
                    "fenced_code",
                    "tables",
                    "nl2br",
                ]
            )

        # =====================================================
        # GEMINI ERROR HANDLING
        # =====================================================

        except Exception as e:

            error = str(e)

            if "429" in error:

                reply = (
                    "⚠️ Gemini API quota has been exceeded. "
                    "Employee and company-policy questions "
                    "can still be answered from the system "
                    "database and knowledge base. "
                    "General AI questions will be available "
                    "again when the Gemini quota resets."
                )

            elif "503" in error:

                reply = (
                    "⚠️ Gemini is currently experiencing "
                    "high demand. Please try again later."
                )

            else:

                reply = f"Gemini Error: {error}"

        # =================================================
        # SHOW AI RESPONSE
        # =================================================

        messages.append({
            "sender": "ai",
            "text": reply
        })

    # =====================================================
    # RENDER CHAT PAGE
    # =====================================================

    return render(
        request,
        "ai_assistant/chat.html",
        {
            "messages": messages
        }
    )