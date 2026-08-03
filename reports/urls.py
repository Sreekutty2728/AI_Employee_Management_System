from django.urls import path

from . import views


urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('employees/', views.employee_report, name='employee_report'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('leave/', views.leave_report, name='leave_report'),
    path('payroll/', views.payroll_report, name='payroll_report'),
    path('departments/', views.department_report, name='department_report'),
    path('<str:report_type>/export/excel/', views.export_excel, name='export_report_excel'),
]
