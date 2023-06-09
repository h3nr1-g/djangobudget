from django.contrib.auth.models import User
from django.db import models

from budgets.models import Budget
from common import models as model_params


class Role(models.Model):
    name = models.CharField(
        **model_params.UNIQUE_CHARFIELD,
    )
    create_account = models.BooleanField(default=False)
    read_account = models.BooleanField(default=False)
    update_account = models.BooleanField(default=False)
    delete_account = models.BooleanField(default=False)

    create_category = models.BooleanField(default=False)
    read_category = models.BooleanField(default=False)
    update_category = models.BooleanField(default=False)
    delete_category = models.BooleanField(default=False)

    create_expense = models.BooleanField(default=False)
    read_expense = models.BooleanField(default=False)
    update_expense = models.BooleanField(default=False)
    delete_expense = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    class Meta:
        unique_together=('user','role', 'budget')