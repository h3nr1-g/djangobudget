from django.contrib.auth.models import User
from django.db import models
from django.utils.datetime_safe import datetime

from common import models as model_params


class Currency(models.Model):
    name = models.CharField(
        **model_params.UNIQUE_CHARFIELD,
        default='Euro',
    )
    symbol = models.CharField(
        **model_params.UNIQUE_CHARFIELD,
        default='€',
    )

    def __str__(self):
        return self.name


class Budget(models.Model):
    name = models.CharField(
        **model_params.UNIQUE_CHARFIELD,
        default='Budget 1',
    )
    owner = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
    )
    note = models.TextField(
        **model_params.NULLABLE
    )
    currency = models.ForeignKey(
        Currency,
        null=True,
        on_delete=models.SET_NULL,
    )
    read_access = models.ManyToManyField(
        User,
        related_name='read',
    )
    write_access = models.ManyToManyField(
        User,
        related_name='write',
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        **model_params.CHARFIELD_PARAMS,
        **model_params.NOT_NULLABLE,
        default='Category 1',
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return self.name

    def descendants(self, elements=[]):
        my_children = list(Category.objects.filter(parent=self))
        if not my_children:
            return
        elements += my_children
        for c in my_children:
            c.descendants(elements)

    class Meta:
        unique_together = ('name', 'budget')


class Account(models.Model):
    name = models.CharField(
        **model_params.CHARFIELD_PARAMS,
        **model_params.NOT_NULLABLE,
        default='Account 1',
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE
    )
    start_balance = models.FloatField(
        **model_params.NOT_NULLABLE,
        default=0
    )
    locked = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = (('budget', 'name'),)

    def __str__(self):
        return self.name

    @property
    def currency(self):
        return self.budget.currency

    @property
    def current_balance(self):
        now = datetime.now()
        return self.balance_at(now)

    @property
    def num_expenses(self):
        return len(Expense.objects.filter(account=self))

    def balance_at(self, ref_dt):
        exp_values = Expense.objects.filter(account=self, created__lte=ref_dt).values_list('amount', flat=True)
        exp_sum = 0 if len(exp_values) < 1 else sum(exp_values)
        return self.start_balance - float(exp_sum)


class Expense(models.Model):
    name = models.CharField(
        **model_params.CHARFIELD_PARAMS,
        **model_params.NOT_NULLABLE,
        default='Expense 1',
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL
    )
    created = models.DateField(
        **model_params.NULLABLE,
        default=None,
    )
    updated = models.DateTimeField(
        **model_params.NULLABLE,
        default=None,
    )
    amount = models.FloatField(
        **model_params.NOT_NULLABLE,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        **model_params.NULLABLE,
        related_name='update_user'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        **model_params.NULLABLE,
    )
    external_reference = models.CharField(
        **model_params.NULLABLE,
        max_length=200,
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        **model_params.NULLABLE,
    )
    note = models.TextField(
        **model_params.NULLABLE
    )

    def __str__(self):
        return self.name


class ExpenseModification(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE
    )
    field_name = models.CharField(
        **model_params.CHARFIELD_PARAMS,
        **model_params.NOT_NULLABLE,
    )
    old_value = models.CharField(
        **model_params.CHARFIELD_PARAMS,
        **model_params.NOT_NULLABLE,
    )
    new_value = models.CharField(
        **model_params.CHARFIELD_PARAMS,
        **model_params.NOT_NULLABLE,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        **model_params.NULLABLE,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
