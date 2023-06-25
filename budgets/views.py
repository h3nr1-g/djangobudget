from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse
from django.utils import formats
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator

from budgets.forms import AccountForm, ExpenseForm, CategoryForm, BudgetEditForm
from budgets.models import Budget, Account, Expense, Category, ExpenseModification
from budgets.tables import BalancesTable, ExpensesTable, AccountsTable, CategoriesTable, ExpenseModificationsTable
from common.models import TranslationEntry
from common.views import AuthenticatedUserView, common_ctx, formpage_ctx


def build_budget_edit_form(request, budget):
    return BudgetEditForm(
        instance=budget,
        data=request.POST if request.POST else None,
    )


def build_account_form(request, budget, instance=None):
    form = AccountForm(
        instance=instance,
        initial={'budget': budget} if instance is None else None,
        data=request.POST if request.POST else None,
    )
    locked_choices = [(True, TranslationEntry.get('YES')), (False, TranslationEntry.get('NO'))]
    form.fields['locked'].widget.choices = locked_choices
    return form


def build_expense_form(request, budget, instance=None):
    initial_data = {}
    account_choices = [(a.id, a.name) for a in Account.objects.filter(budget=budget, locked=False).order_by('name')]
    if instance:
        initial_data['budget'] = budget
        initial_data['account'] = instance.account
        account_choices.append((instance.account.id, instance.account.name,))

    form = ExpenseForm(
        instance=instance,
        initial=initial_data if instance else None,
        data=request.POST if request.POST else None,
    )

    ajax_url = '{}?budget={}'.format(reverse('ajax_lookup', kwargs={'channel': 'categories'}), budget.id)
    form.fields['category'].widget.plugin_options['source'] = ajax_url
    form.fields['account'].choices = account_choices
    form.fields['account'].widget.choices = account_choices

    return form


def build_category_form(request, budget, instance=None):
    form = CategoryForm(
        instance=instance,
        data=request.POST if request.POST else None,
    )
    category_choices = [(None, None)] + [(c.id, c.name) for c in
                                         Category.objects.filter(budget=budget).order_by('name')]
    form.fields['parent'].choices = category_choices
    form.fields['parent'].widget.choices = category_choices

    return form


def permission_check(budget, user, permission):
    param = f'{permission}_access'
    return user.is_superuser or user == budget.owner or user in getattr(budget, param).all()


class BudgetView(AuthenticatedUserView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        budget = get_object_or_404(Budget, id=kwargs['bid'])
        if permission_check(budget, request.user, 'read'):
            return super(BudgetView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied(TranslationEntry.get('PERMISSION_DENIED'))


class BudgetSelectView(AuthenticatedUserView):
    def get(self, request):
        return render(request, 'budgets/select.html', common_ctx(request))


class DashboardView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        ctx = {
            **common_ctx(request, budget),
            'title': 'Dashboard',
            'balance_table': BalancesTable(Account.objects.filter(budget=budget, locked=False).order_by('name')),
            'balance_table_title': TranslationEntry.get('BALANCE'),
            'expense_table': ExpensesTable(Expense.objects.filter(budget=budget).order_by('-created')),
            'expense_table_title': TranslationEntry.get('EXPENSES'),
        }

        return render(request, 'budgets/dashboard/dashboard.html', ctx)


class DashboardDataView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        return JsonResponse({
            'stats': self.get_stats_data(budget),
            'charts': self.get_chart_data(budget)
        })

    def get_stats_data(self, budget):
        accounts = Account.objects.filter(budget=budget, locked=False)
        expenses = sum([e.amount for e in Expense.objects.filter(account__in=accounts)])
        total_budget = sum([a.start_balance for a in accounts])
        return {
            'expenses': formats.number_format(expenses, decimal_pos=2, use_l10n=True),
            'remaining_budget': formats.number_format(total_budget - expenses, decimal_pos=2, use_l10n=True),
            'total_budget': formats.number_format(total_budget, decimal_pos=2, use_l10n=True),
            'num_accounts': len(accounts),
        }

    def get_chart_data(self, budget):
        return {
            'history': self.get_history_data(budget),
            'distribution': self.get_dist_data(budget),
        }

    def get_dist_data(self, budget):
        return []

    def get_history_data(self, budget):
        series = []
        accounts = Account.objects.filter(budget=budget, locked=False).order_by('id')
        account_names = [a.name for a in accounts]
        expenses = Expense.objects.filter(account__in=accounts)
        for e in expenses.order_by('created'):
            entry = {'x': e.created.strftime('%Y/%m/%d'), 'expense': e.amount}
            for a in accounts:
                entry[f'acc_{a.id}'] = a.balance_at(e.created)
            series.append(entry)

        lang = settings.LANGUAGE_CODE
        lang = lang.split('-')[0] if '-' in lang else lang
        return {
            'series': series,
            'ykeys': ['expense'] + [f'acc_{a.id}' for a in accounts],
            'labels': [TranslationEntry.get('EXPENSES'), ] + account_names,
            'lang': lang
        }


class AccountAddView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        ctx = self.build_ctx(request, budget)
        return render(request, 'common/formpage.html', ctx)

    def post(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        form = build_account_form(request, budget)
        valid = form.is_valid()
        name_valid = len(Account.objects.filter(budget=budget, name=form.cleaned_data['name'])) < 1 if valid else None
        if valid and name_valid:
            account = form.save(commit=False)
            account.budget = budget
            account.save()
            messages.success(request, TranslationEntry.get('ACCOUNT_CREATED'))
            return redirect('budgets:account_details', bid=budget.id, aid=account.id)
        elif valid:
            form.errors['name'] = [TranslationEntry.get('NAME_ALREADY_IN_USE')]
        messages.error(request, TranslationEntry.get('ACCOUNT_CREATION_FAILED'))
        ctx = self.build_ctx(request, budget, form)
        return render(request, 'common/formpage.html', ctx)

    def build_ctx(self, request, budget, form=None):
        used_form = form or build_account_form(request, budget)
        return {
            'title': TranslationEntry.get('CREATE_ACCOUNT', 'de'),
            **formpage_ctx(request, budget, used_form, reverse('budgets:accounts_add', args=(budget.id,)))
        }


class AccountsDetailsView(BudgetView):
    def get(self, request, bid, aid):
        budget = get_object_or_404(Budget, id=bid)
        account = get_object_or_404(Account, id=aid)
        ctx = self.build_ctx(request, budget, account)
        return render(request, 'budgets/account.html', ctx)

    def post(self, request, bid, aid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()
        account = get_object_or_404(Account, id=aid)

        form = build_account_form(request, budget, account)
        if form.is_valid():
            new_name = form.cleaned_data.get('name')
            if 'name' in form.changed_data and len(Account.objects.filter(budget=budget, name=new_name)) > 0:
                form.errors['name'] = [TranslationEntry.get('NAME_ALREADY_IN_USE')]
                messages.error(request, TranslationEntry.get('ACCOUNT_UPDATE_FAILED'))
            else:
                account = form.save(commit=False)
                account.budget = budget
                account.save()
                messages.success(request, TranslationEntry.get('ACCOUNT_UPDATED'))
        else:
            messages.error(request, TranslationEntry.get('ACCOUNT_UPDATE_FAILED'))

        ctx = self.build_ctx(request, budget, account, form)
        return render(request, 'budgets/account.html', ctx)

    def delete(self, request, bid, aid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        account = get_object_or_404(Account, id=aid)
        account.delete()
        messages.success(request, TranslationEntry.get('ACCOUNT_DELETED'))
        return HttpResponse()

    def build_ctx(self, request, budget, account, form=None):
        used_form = form or build_account_form(request, budget, account)
        expenses = Expense.objects.filter(account=account).order_by('-created')
        return {
            'title': account.name,
            'table_title': TranslationEntry.get('EXPENSES'),
            'table': ExpensesTable(expenses),
            'spent': sum(expenses.values_list('amount', flat=True)),
            'locked': account.locked,
            'remaining': account.balance_at(datetime.now()),
            **formpage_ctx(request, budget, used_form, reverse('budgets:account_details', args=(budget.id, account.id)))
        }


class AccountsTableView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        ctx = {
            'table': AccountsTable(Account.objects.filter(budget=budget).order_by('name')),
            'title': TranslationEntry.get('ACCOUNTS', 'de'),
            **common_ctx(request, budget),
        }
        return render(request, 'common/tables/tablepage.html', ctx)


class ExpenseAddView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()
        ctx = self.build_ctx(request, budget)
        return render(request, 'common/formpage.html', ctx)

    def post(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        form = build_expense_form(request, budget)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.author = request.user
            exp.updated_by = request.user
            exp.budget = budget
            exp.save()

            messages.success(request, TranslationEntry.get('EXPENSE_CREATED'))
            return redirect('budgets:expense_details', bid=bid, eid=exp.id)
        messages.error(request, TranslationEntry.get('EXPENSE_CREATION_FAILED'))
        ctx = self.build_ctx(request, budget, form)
        return render(request, 'common/formpage.html', ctx)

    def build_ctx(self, request, budget, form=None):
        used_form = form or build_expense_form(request, budget)
        return {
            'title': TranslationEntry.get('CREATE_EXPENSE', 'de'),
            **formpage_ctx(request, budget, used_form, reverse('budgets:expenses_add', args=(budget.id,)))
        }


class ExpenseDetailsView(BudgetView):
    def get(self, request, bid, eid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'read'):
            raise PermissionDenied()

        expense = get_object_or_404(Expense, id=eid)
        ctx = self.build_ctx(request, budget, expense)
        return render(request, 'budgets/expense.html', ctx)

    def post(self, request, bid, eid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        expense = get_object_or_404(Expense, id=eid)
        form = build_expense_form(request, budget, expense)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.updated_by = request.user
            expense.save()
            form = None
            messages.success(request, TranslationEntry.get('EXPENSE_UPDATED'))
        else:
            messages.error(request, TranslationEntry.get('EXPENSE_UPDATE_FAILED'))
        ctx = self.build_ctx(request, budget, expense, form)
        return render(request, 'budgets/expense.html', ctx)

    def delete(self, request, bid, eid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        expense = get_object_or_404(Expense, id=eid)
        expense.delete()
        messages.success(request, TranslationEntry.get('EXPENSE_DELETED'))
        return HttpResponse()

    def build_ctx(self, request, budget, expense, form=None):
        used_form = form or build_expense_form(request, budget, expense)
        return {
            **formpage_ctx(request, budget, used_form,
                           reverse('budgets:expense_details', args=(budget.id, expense.id))),
            'title': expense.name,
            'table_title': TranslationEntry.get('HISTORY'),
            'table': ExpenseModificationsTable(
                ExpenseModification.objects.filter(expense=expense).order_by('-timestamp')
            ),
        }


class ExpensesTableView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        ctx = {
            **common_ctx(request, budget),
            'table': ExpensesTable(Expense.objects.filter(budget=budget).order_by('-created')),
            'title': TranslationEntry.get('EXPENSES', 'de'),
        }
        return render(request, 'common/tables/tablepage.html', ctx)


class CategoryAddView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        ctx = self.build_ctx(request, budget)
        return render(request, 'common/formpage.html', ctx)

    def post(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        form = build_category_form(request, budget)
        if form.is_valid():
            category = form.save(commit=False)
            category.budget = budget
            category.save()
            messages.success(request, TranslationEntry.get('CATEGORY_CREATED'))
            return redirect('budgets:category_details', bid=budget.id, cid=category.id)
        messages.error(request, TranslationEntry.get('CATEGORY_CREATION_FAILED'))
        ctx = self.build_ctx(request, budget, form)
        return render(request, 'common/formpage.html', ctx)

    def build_ctx(self, request, budget, form=None):
        used_form = form or build_category_form(request, budget)
        return {
            'title': TranslationEntry.get('CREATE_CATEGORY', 'de'),
            **formpage_ctx(request, budget, used_form, reverse('budgets:categories_add', args=(budget.id,)))
        }


class CategoryDetailsView(BudgetView):
    def get(self, request, bid, cid):
        budget = get_object_or_404(Budget, id=bid)
        category = get_object_or_404(Category, id=cid)
        ctx = self.build_ctx(request, budget, category)
        return render(request, 'budgets/category.html', ctx)

    def post(self, request, bid, cid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        category = get_object_or_404(Category, id=cid)
        form = build_category_form(request, budget, category)
        if form.is_valid():
            category = form.save(commit=False)
            category.budget = budget
            category.save()
            messages.success(request, TranslationEntry.get('CATEGORY_UPDATED'))
        else:
            messages.error(request, TranslationEntry.get('CATEGORY_UPDATE_FAILED'))

        ctx = self.build_ctx(request, category, category, form)
        return render(request, 'budgets/category.html', ctx)

    def delete(self, request, bid, cid):
        budget = get_object_or_404(Budget, id=bid)
        if not permission_check(budget, request.user, 'write'):
            raise PermissionDenied()

        category = get_object_or_404(Category, id=cid)
        category.delete()
        messages.success(request, TranslationEntry.get('CATEGORY_DELETED'))
        return HttpResponse()

    def build_ctx(self, request, budget, category, form=None):
        used_form = form or build_category_form(request, budget, category)
        categories = [category]
        category.descendants(categories)
        expenses = Expense.objects.filter(category__in=categories).order_by('-created')
        return {
            'title': category.name,
            'table_title': TranslationEntry.get('EXPENSES'),
            'table': ExpensesTable(expenses),
            'amount': sum([e.amount for e in expenses]),
            'count': len(expenses),
            **formpage_ctx(request, budget, used_form,
                           reverse('budgets:category_details', args=(budget.id, category.id)))
        }


class CategoriesTableView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        ctx = {
            **common_ctx(request, budget),
            'table': CategoriesTable(Category.objects.filter(budget=budget).order_by('name')),
            'title': TranslationEntry.get('CATEGORIES', 'de')
        }
        return render(request, 'common/tables/tablepage.html', ctx)


class BudgetEditView(BudgetView):
    def get(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not request.user.is_superuser and request.user != budget.owner:
            raise PermissionDenied()

        ctx = self.build_ctx(request, budget)
        return render(request, 'common/formpage.html', ctx)

    def post(self, request, bid):
        budget = get_object_or_404(Budget, id=bid)
        if not request.user.is_superuser and request.user != budget.owner:
            raise PermissionDenied()

        form = build_budget_edit_form(request, budget)
        if form.is_valid():
            form.save()
            messages.success(request, TranslationEntry.get('BUDGET_UPDATED'))
        else:
            messages.error(request, TranslationEntry.get('BUDGET_UPDATE_FAILED'))
        ctx = self.build_ctx(request, budget, form)
        return render(request, 'common/formpage.html', ctx)

    def build_ctx(self, request, budget, form=None):
        used_form = form or build_budget_edit_form(request, budget)
        return {
            'title': budget.name,
            **formpage_ctx(request, budget, used_form, reverse('budgets:edit', args=(budget.id,)))
        }
