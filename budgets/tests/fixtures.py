from budgets.models import Budget, Currency


def create_budgets(owner=None):
    Budget.objects.create(name='Budget 1', owner=owner)
    Budget.objects.create(name='Budget 2', owner=owner)
    Budget.objects.create(name='Budget 3', owner=owner)
    Budget.objects.create(name='Budget 4', owner=owner)


def create_currencies():
    Currency.objects.create(name='Euro', symbol='€')
    Currency.objects.create(name='Dollar', symbol='$')
    Currency.objects.create(name='Yen', symbol='¥')
