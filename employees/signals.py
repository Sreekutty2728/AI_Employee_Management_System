from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Employee


DEFAULT_EMPLOYEE_PASSWORD = 'Welcome@123'


@receiver(post_save, sender=Employee)
def create_employee_user(sender, instance, created, **kwargs):

    if not created or instance.user_id:
        return

    User = get_user_model()

    user, created_user = User.objects.get_or_create(
        username=instance.employee_id,
        defaults={
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'is_active': True,
            'password': make_password(DEFAULT_EMPLOYEE_PASSWORD),
        },
    )

    if created_user:
        user.set_password(DEFAULT_EMPLOYEE_PASSWORD)
        user.is_active = True
        user.save()

    Employee.objects.filter(pk=instance.pk).update(user=user)