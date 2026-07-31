from django.urls import path
from . import views


urlpatterns = [
    path('', views.leave_list, name='leave_list'),
    path('add/', views.add_leave, name='add_leave'),
    path('edit/<int:id>/', views.edit_leave, name='edit_leave'),
    path('delete/<int:id>/', views.delete_leave, name='delete_leave'),
]
