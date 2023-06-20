from django_tables2 import tables, TemplateColumn, Column

from budgets.models import Account, Expense, Category, ExpenseModification, Budget


def make_actions_col(details_url_name, delelte_url_name=None, show_delete=True, exlcude_record_budget=False, **kwargs):
    bid = '' if exlcude_record_budget else 'record.budget.id'
    details = \
        '<a href="{% url "' + details_url_name + '" ' + bid + ' record.id %}">' \
        '<button class="btn btn-sm btn-primary"><i class="fa-solid fa-circle-info"></i></button>' \
        '</a>'

    delete = \
        '<a href="{% url "' + (delelte_url_name or '') + '" record.budget.id record.id %}">' \
        '<button style="margin-left: 10px;" class="btn btn-sm btn-danger"><i class="fa-solid fa-trash"></i></button>' \
        '</a>'

    return TemplateColumn(
        details + (delete if show_delete else ''),
        verbose_name='',
        **kwargs
    )


class BalancesTable(tables.Table):
    name = Column(
        verbose_name='NAME',
        attrs={'th': {'class': 'translate'}},
    )
    current_balance = TemplateColumn(
        '{{record.current_balance|floatformat:2}} {{record.currency.symbol}}',
        verbose_name='CURRENT_BALANCE',
        attrs={'th': {'class': 'translate'}}
    )
    actions = make_actions_col('budgets:account_details', show_delete=False)

    class Meta:
        model = Account
        template_name = 'django_tables2/bootstrap4.html'
        sequence = (
            'name',
            'current_balance',
            'actions'
        )
        exclude = [
            f.name for f in Account._meta.get_fields()
            if f.name not in ('name', 'current_balance')
        ]


class AccountsTable(tables.Table):
    name = Column(
        verbose_name='NAME',
        attrs={'th': {'class': 'translate'}}
    )
    current_balance = TemplateColumn(
        '{{record.current_balance|floatformat:2}} {{record.currency.symbol}}',
        verbose_name='CURRENT_BALANCE',
        attrs={'th': {'class': 'translate'}}
    )
    actions = make_actions_col('budgets:account_details', show_delete=False)
    num_expenses = Column(
        verbose_name='NUM_EXPENSES',
        attrs={'th': {'class': 'translate'}},
    )
    locked = TemplateColumn(
        '{%if record.locked %}'
        '<span class="translate text-danger font-weight-bold">YES</span>'
        '{% else %}'
        '<span class="translate text-success font-weight-bold">NO</span>'
        '{% endif %}',
        verbose_name='LOCKED',
        attrs={
            'th': {'class': 'translate'},
        },
    )

    class Meta:
        model = Account
        template_name = 'django_tables2/bootstrap4.html'
        sequence = (
            'name',
            'current_balance',
            'num_expenses',
            'locked',
            'actions'
        )
        exclude = [
            f.name for f in Account._meta.get_fields()
            if f.name not in ('name', 'current_balance', 'locked', 'num_expenses',)
        ]


class ExpensesTable(tables.Table):
    created = Column(
        verbose_name='CREATION_DATE',
        attrs={'th': {'class': 'translate'}},
    )
    author = Column(
        verbose_name='AUTHOR',
        attrs={'th': {'class': 'translate'}},
    )
    name = Column(
        verbose_name='NAME',
        attrs={'th': {'class': 'translate'}},
    )
    amount = TemplateColumn(
        '{{record.amount|floatformat:2 }} {{record.account.currency.symbol}}',
        verbose_name='AMOUNT',
        attrs={'th': {'class': 'translate'}},
    )
    category = TemplateColumn(
        '<a href="{% url "budgets:category_details" record.budget.id record.category.id %}">{{ record.category }}</a>',
        verbose_name='CATEGORY',
        attrs={'th': {'class': 'translate'}},
    )
    actions = make_actions_col('budgets:expense_details', show_delete=False)

    class Meta:
        model = Expense
        template_name = 'django_tables2/bootstrap4.html'
        sequence = (
            'created',
            'author',
            'name',
            'category',
            'amount',
            'actions'
        )
        exclude = [
            f.name for f in Expense._meta.get_fields()
            if f.name not in ('created', 'author', 'name', 'category', 'amount')
        ]


class CategoriesTable(tables.Table):
    name = Column(
        verbose_name='NAME',
        attrs={'th': {'class': 'translate'}},
    )
    actions = make_actions_col('budgets:category_details', show_delete=False)

    class Meta:
        model = Category
        template_name = 'django_tables2/bootstrap4.html'
        sequence = (
            'name',
            'actions'
        )
        exclude = [
            f.name for f in Category._meta.get_fields()
            if f.name not in ('name',)
        ]


class ExpenseModificationsTable(tables.Table):
    timestamp = Column(
        verbose_name='TIMESTAMP',
        attrs={'th': {'class': 'translate'}},
    )
    updated_by = Column(
        verbose_name='UPDATED_BY',
        attrs={'th': {'class': 'translate'}},
    )
    field_name = Column(
        verbose_name='FIELD_NAME',
        attrs={'th': {'class': 'translate'}},
    )
    old_value = TemplateColumn(
        '<span class="text-danger">{{value}}</span>',
        verbose_name='OLD_VALUE',
        attrs={'th': {'class': 'translate'}},
    )
    new_value = TemplateColumn(
        '<span class="text-success">{{value}}</span>',
        verbose_name='NEW_VALUE',
        attrs={'th': {'class': 'translate'}},
    )

    class Meta:
        orderable = False
        model = ExpenseModification
        template_name = 'django_tables2/bootstrap4.html'
        sequence = (
            'timestamp',
            'updated_by',
            'field_name',
            'old_value',
            'new_value',
        )
        exclude = [
            f.name for f in Category._meta.get_fields()
            if f.name not in (
                'timestamp',
                'updated_by',
                'field_name',
                'old_value',
                'new_value',
            )
        ]


class BudgetsTable(tables.Table):
    actions = make_actions_col('budgets:dashboard', show_delete=False, exlcude_record_budget=True)

    class Meta:
        model = Budget
        template_name = 'django_tables2/bootstrap4.html'
        sequence = (
            'name',
            'note',
            'currency',
            'actions',
        )
        exclude = [
            'id',
            'owner'
        ]
