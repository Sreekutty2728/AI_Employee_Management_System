from django.db import models


class Department(models.Model):

    department_name = models.CharField(max_length=100)

    department_code = models.CharField(
        max_length=20,
        unique=True
    )

    department_head = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="Active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.department_name