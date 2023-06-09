from django.contrib import admin

# Register your models here.
from budgets.models import Currency, Budget, Category, Account, Expense, ExpenseModification

admin.site.register(Currency)
admin.site.register(Budget)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Expense)
admin.site.register(ExpenseModification)
