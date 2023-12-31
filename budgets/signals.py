from django.db.models.signals import pre_save
from django.dispatch import receiver

from budgets.models import Expense, ExpenseModification


@receiver(pre_save, sender=Expense)
def log_modification(instance, **kwargs):
    if not instance.id:
        return

    old = Expense.objects.get(id=instance.id)
    for field in ['category', 'amount', 'name', 'note', 'created']:
        old_val = getattr(old, field)
        new_val = getattr(instance, field)
        if old_val != new_val:
            ExpenseModification.objects.create(
                expense=instance,
                field_name=field,
                old_value=str(old_val) if old_val is not None else '',
                new_value=str(new_val) if new_val is not None else '',
                updated_by=instance.updated_by,
            )
