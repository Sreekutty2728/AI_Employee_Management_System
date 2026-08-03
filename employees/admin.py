from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'department', 'designation', 'user', 'is_active')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email')
    readonly_fields = ('user',)
    exclude = ('user',)
