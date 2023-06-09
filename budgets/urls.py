from django.urls import path

from budgets.views import DashboardView, AccountAddView, AccountsTableView, ExpensesTableView, ExpenseAddView, \
    ExpenseDetailsView, DashboardDataView, AccountsDetailsView, CategoryAddView, CategoryDetailsView, \
    CategoriesTableView, BudgetEditView

urlpatterns = [
    path('<int:bid>/edit', BudgetEditView.as_view(), name='edit'),

    path('<int:bid>/dashboard', DashboardView.as_view(), name='dashboard'),
    path('<int:bid>/dashboard/data', DashboardDataView.as_view(), name='dashboard_data'),

    path('<int:bid>/accounts/add', AccountAddView.as_view(), name='accounts_add'),
    path('<int:bid>/accounts/all', AccountsTableView.as_view(), name='accounts_table'),
    path('<int:bid>/accounts/<int:aid>', AccountsDetailsView.as_view(), name='account_details'),

    path('<int:bid>/categories/add', CategoryAddView.as_view(), name='categories_add'),
    path('<int:bid>/categories/all', CategoriesTableView.as_view(), name='categories_table'),
    path('<int:bid>/categories/<int:cid>', CategoryDetailsView.as_view(), name='category_details'),

    path('<int:bid>/expenses/add', ExpenseAddView.as_view(), name='expenses_add'),
    path('<int:bid>/expenses/all', ExpensesTableView.as_view(), name='expenses_table'),
    path('<int:bid>/expenses/<int:eid>', ExpenseDetailsView.as_view(), name='expense_details'),
]
