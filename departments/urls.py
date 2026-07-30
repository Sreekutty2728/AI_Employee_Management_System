from django.urls import path
from . import views

urlpatterns = [

    # View All Departments
    path(
        '',
        views.department_list,
        name='department_list'
    ),

    # Add Department
    path(
        'add/',
        views.add_department,
        name='add_department'
    ),

    # Edit Department
    path(
        'edit/<int:id>/',
        views.edit_department,
        name='edit_department'
    ),

    # Delete Department
    path(
        'delete/<int:id>/',
        views.delete_department,
        name='delete_department'
    ),

]