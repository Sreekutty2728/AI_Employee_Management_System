from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion


DEFAULT_EMPLOYEE_PASSWORD = 'Welcome@123'


def create_accounts_for_existing_employees(apps, schema_editor):
    Employee = apps.get_model('employees', 'Employee')
    User = apps.get_model('auth', 'User')
    for employee in Employee.objects.filter(user__isnull=True):
        user, _ = User.objects.get_or_create(
            username=employee.employee_id,
            defaults={
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'is_active': employee.is_active,
                'password': make_password(DEFAULT_EMPLOYEE_PASSWORD),
            },
        )
        employee.user_id = user.pk
        employee.save(update_fields=['user'])


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employees', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(create_accounts_for_existing_employees, migrations.RunPython.noop),
    ]
