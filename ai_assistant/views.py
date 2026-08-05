from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employees.models import Employee


@login_required
def chat(request):
    messages = []

    # Get the logged-in employee
    employee = Employee.objects.get(user=request.user)

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        # Show employee message
        messages.append({
            "sender": "user",
            "text": question
        })

        q = question.lower()

        # HR Questions
        if "salary" in q:
            reply = f"Your monthly salary is ₹{employee.salary}."

        elif "employee id" in q:
            reply = f"Your Employee ID is {employee.employee_id}."

        elif "department" in q:
            reply = f"You are working in the {employee.department} department."

        elif "designation" in q:
            reply = f"Your designation is {employee.designation}."

        elif "email" in q:
            reply = f"Your email address is {employee.email}."

        elif "phone" in q:
            reply = f"Your phone number is {employee.phone}."

        elif "joining" in q or "date of joining" in q:
            reply = f"Your date of joining is {employee.date_of_joining}."

        elif "name" in q:
            reply = f"Your name is {employee.first_name} {employee.last_name}."

        elif "attendance" in q:
            reply = "Attendance information will be connected to the database in the next step."

        elif "leave" in q:
            reply = "Leave information will be connected to the database in the next step."

        elif "hello" in q or "hi" in q:
            reply = f"Hello {employee.first_name}! How can I help you today?"

        else:
            reply = "Sorry, I couldn't understand your question."

        # Show AI reply
        messages.append({
            "sender": "ai",
            "text": reply
        })

    return render(request, "ai_assistant/chat.html", {
        "messages": messages
    })