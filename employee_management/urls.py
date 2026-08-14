from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),

    # Login Module
    path('', include('accounts.urls')),

    # Admin Dashboard
    path('admin-dashboard/', include('admin_panel.urls')),

    # Employee Module
    path('employees/', include('employees.urls')),

    # Department Module
    path('departments/', include('departments.urls')),

    # Attendance Module
    path('attendance/', include('attendance.urls')),

    # Leave Management Module
    path('leave-management/', include('leave_management.urls')),

    # Payroll Module
    path('payroll/', include('payroll.urls')),

    # Reports Module
    path('reports/', include('reports.urls')),

    # AI Assistant
    path('ai/', include('ai_assistant.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )