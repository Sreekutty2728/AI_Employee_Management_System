from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employees.models import Employee
import markdown

import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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
            reply = f"Hello {employee.first_name}! How can I help you today."

        else:
            try:
                prompt = f"""
You are an AI HR Assistant for an Employee Management System.

Answer the user's question in a professional and easy-to-read format.

Rules:
- Use headings.
- Use bullet points.
- Keep paragraphs short.
- Highlight important terms using **bold**.
- Give examples where appropriate.
- Do not answer in one long paragraph.

Question:
{question}
"""

                response = client.models.generate_content(
                model="models/gemini-3.6-flash",
                contents=prompt,
)

                reply = markdown.markdown(
    response.text,
    extensions=[
        "fenced_code",
        "tables",
        "nl2br",
    ]
)
            except Exception as e:
                error = str(e)

                if "503" in error:
                    reply = (
                        "⚠️ Gemini is currently experiencing high demand. "
                        "Please try again in a few moments."
                    )
                else:
                    reply = f"Gemini Error: {error}"

        # Show AI reply
        messages.append({
            "sender": "ai",
            "text": reply
        })

    return render(request, "ai_assistant/chat.html", {
        "messages": messages
    })