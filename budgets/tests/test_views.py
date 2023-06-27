import datetime
import json
from datetime import datetime as dt

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django_webtest import WebTest

from budgets.models import Budget, Account, Expense, Currency, Category, ExpenseModification

USER_PASSWORD = '12345'


class InstanceCrudSuite:
    def _get_form_or_die(self, user):
        resp = self.app.get(self.url, user=user, status='*')
        self.assertEqual(200, resp.status_code)
        return resp.form

    def _run_modification(self, param_dict, user, exp_result_message, exp_status_code):
        form = self._get_form_or_die(user)
        for field, value in param_dict.items():
            form[field] = value
        resp = form.submit(status='*')
        self.assertEqual(exp_status_code, resp.status_code)
        if exp_result_message:
            self.assertIn(exp_result_message, resp.content.decode())

    def check_modifications(self, modifications, user, exp_result_message, exp_status_code=200):
        for param_dict in modifications:
            self._run_modification(param_dict, user, exp_result_message, exp_status_code)

    def check_deletion(self, url, user, exp_status_code=200):
        self.client.login(username=user.username, password=USER_PASSWORD)
        resp = self.client.delete(url)
        self.assertEqual(exp_status_code, resp.status_code)

    def check_creation(self, creation_params, user, exp_result_message, exp_status_code=302):
        self.check_modifications(creation_params, user, exp_result_message, exp_status_code)


class BudgetSetup:
    def prepare_budget(self):
        self.budget = Budget.objects.create(
            name='budget1',
            currency=Currency.objects.create(name='Dollar', symbol='$')
        )
        self.owner = User.objects.create_user(username='user1', password=USER_PASSWORD)
        self.ro_user = User.objects.create_user(username='user2', password=USER_PASSWORD)
        self.rw_user = User.objects.create_user(username='user3', password=USER_PASSWORD)
        self.budget.owner = self.owner
        self.budget.read_access.add(self.ro_user)
        self.budget.read_access.add(self.rw_user)
        self.budget.write_access.add(self.rw_user)
        self.budget.save()


class BudgetSelectViewTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='user1', password=USER_PASSWORD)
        self.budget1 = Budget.objects.create(name='budget1')
        self.budget2 = Budget.objects.create(name='budget2', note='XXXXX')
        self.url = reverse('index')

    def test_access_as_anonymous_user(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
        self.assertIn('/auth/login', resp.headers.get('location'))

    def test_access_as_unrelated_user(self):
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertNotIn(self.budget1.name, resp.content.decode())
        self.assertNotIn(self.budget2.name, resp.content.decode())

    def test_as_budget_owner(self):
        self.budget2.owner = self.test_user
        self.budget2.save()
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertNotIn(self.budget1.name, resp.content.decode())
        self.assertIn(self.budget2.name, resp.content.decode())
        self.assertIn(self.budget2.note, resp.content.decode())

    def test_as_ro_user(self):
        self.budget2.read_access.add(self.test_user)
        self.budget2.save()
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertNotIn(self.budget1.name, resp.content.decode())
        self.assertIn(self.budget2.name, resp.content.decode())
        self.assertIn(self.budget2.note, resp.content.decode())


class DashboardViewTest(TestCase):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1')
        self.test_user = User.objects.create_user(username='user1', password=USER_PASSWORD)
        self.url = reverse('budgets:dashboard', kwargs={'bid': self.budget.id})

    def test_access_as_anonymous_user(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
        self.assertIn('/auth/login', resp.headers.get('location'))

    def test_access_as_unauthorized_user(self):
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)

    def test_access_as_owner(self):
        self.budget.owner = self.test_user
        self.budget.save()
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertIn(self.budget.name, resp.content.decode())

    def test_as_ro_user(self):
        self.budget.read_access.add(self.test_user)
        self.budget.save()
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertIn(self.budget.name, resp.content.decode())


class DashboardDataViewTest(TestCase):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1')
        self.test_user = User.objects.create_user(username='user1', password=USER_PASSWORD)
        self.url = reverse('budgets:dashboard_data', kwargs={'bid': self.budget.id})

    def test_access_as_anonymous_user(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
        self.assertIn('/auth/login', resp.headers.get('location'))

    def test_access_as_unauthorized_user(self):
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)

    def test_access_as_owner(self):
        self.budget.owner = self.test_user
        self.budget.save()
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)

    def test_as_ro_user(self):
        self.budget.read_access.add(self.test_user)
        self.budget.save()
        self.client.login(username=self.test_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        return resp

    def test_dashboard_data_retrieval(self):
        a1 = Account.objects.create(name='a1', budget=self.budget, start_balance=500, locked=False)
        a2 = Account.objects.create(name='a2', budget=self.budget, start_balance=500, locked=False)
        a3 = Account.objects.create(name='a3', budget=self.budget, start_balance=500, locked=True)

        year = dt.now().year
        Expense.objects.create(name='e1', budget=self.budget, created=dt(year, 1, 1), amount=100, account=a1)
        Expense.objects.create(name='e2', budget=self.budget, created=dt(year, 1, 10), amount=100, account=a1)
        Expense.objects.create(name='e3', budget=self.budget, created=dt(year, 1, 30), amount=100, account=a1)
        Expense.objects.create(name='e4', budget=self.budget, created=dt(year, 5, 1), amount=100, account=a2)
        Expense.objects.create(name='e5', budget=self.budget, created=dt(year, 5, 10), amount=100, account=a3)
        Expense.objects.create(name='e6', budget=self.budget, created=dt(year, 5, 30), amount=100, account=a3)

        resp = self.test_as_ro_user()
        data = json.loads(resp.content.decode())

        self.assertIn('stats', data)
        stats = data.get('stats')
        self.assertEqual('400.00', stats['expenses'])
        self.assertEqual('600.00', stats['remaining_budget'])
        self.assertEqual('1000.00', stats['total_budget'])
        self.assertEqual(2, stats['num_accounts'])

        self.assertIn('charts', data)
        charts = data.get('charts')
        self.assertIn('series', charts['history'])
        self.assertIn('series', charts['history'])


class AccountAddViewTest(WebTest, BudgetSetup, InstanceCrudSuite):
    def setUp(self):
        self.prepare_budget()
        self.url = reverse('budgets:accounts_add', kwargs={'bid': self.budget.id})
        self.valid_parameters = [
            {'name': 'Account123', 'start_balance': '600'},
        ]
        self.invalid_parameters = [
            {'name': '', 'start_balance': '600'},
        ]
        self.success_message = 'ACCOUNT_CREATED'
        self.error_message = 'ACCOUNT_CREATION_FAILED'

    def test_valid_creations_as_owner(self):
        self.check_creation(self.valid_parameters, self.owner, None)

    def test_valid_creations_as_rw_user(self):
        self.check_creation(self.valid_parameters, self.owner, None)

    def test_invalid_creations_as_owner(self):
        self.check_creation(self.invalid_parameters, self.owner, self.error_message, 200)

    def test_invalid_creations_as_rw_user(self):
        self.check_creation(self.invalid_parameters, self.rw_user, self.error_message, 200)

    def test_creation_as_ro_user(self):
        self.client.login(username=self.ro_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)


class AccountsDetailsViewTest(WebTest, BudgetSetup, InstanceCrudSuite):
    def setUp(self):
        self.prepare_budget()
        self.model_instance = Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        self.url = reverse('budgets:account_details', kwargs={'bid': self.budget.id, 'aid': self.model_instance.id})
        self.valid_modifications = [
            {'name': 'New Name 123'},
            {'start_balance': 600}
        ]
        self.invalid_modifications = [
            {'name': ''}
        ]
        self.success_message = 'ACCOUNT_UPDATED'
        self.error_message = 'ACCOUNT_UPDATE_FAILED'

    def test_valid_modifications_as_owner(self):
        self.check_modifications(self.valid_modifications, self.owner, self.success_message)

    def test_valid_modifications_as_rw_user(self):
        self.check_modifications(self.valid_modifications, self.owner, self.success_message)

    def test_valid_modifications_as_ro_user(self):
        self.check_modifications(self.valid_modifications, self.ro_user, 'PERMISSION_DENIED', 403)

    def test_invalid_modifications_as_owner(self):
        self.check_modifications(self.invalid_modifications, self.owner, self.error_message)

    def test_invalid_modifications_as_rw_user(self):
        self.check_modifications(self.invalid_modifications, self.rw_user, self.error_message)

    def test_invalid_modifications_as_ro_user(self):
        self.check_modifications(self.invalid_modifications, self.ro_user, 'PERMISSION_DENIED', 403)

    def test_name_duplicate(self):
        Account.objects.create(budget=self.budget, name='account2', start_balance=1000)
        self.check_modifications([{'name': 'account2'}, ], self.rw_user, 'NAME_ALREADY_IN_USE')

    def test_delete_as_owner(self):
        self.check_deletion(self.url, self.owner, 200)
        self.assertEqual(0, len(type(self.model_instance).objects.filter(id=self.model_instance.id)))

    def test_delete_as_rw_user(self):
        self.check_deletion(self.url, self.rw_user, 200)
        self.assertEqual(0, len(type(self.model_instance).objects.filter(id=self.model_instance.id)))

    def test_delete_as_ro_user(self):
        self.check_deletion(self.url, self.ro_user, 403)


class AccountsTableViewTest(TestCase, BudgetSetup):
    def setUp(self):
        self.prepare_budget()
        Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        Account.objects.create(budget=self.budget, name='account2', start_balance=1000)
        self.url = reverse('budgets:accounts_table', kwargs={'bid': self.budget.id})
        self.model_class = Account

    def test_listing(self):
        self.client.login(username=self.owner.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        for inst in self.model_class.objects.filter(budget=self.budget):
            self.assertIn(str(inst), resp.content.decode())


class ExpenseDetailsView(WebTest, BudgetSetup, InstanceCrudSuite):
    def setUp(self):
        self.prepare_budget()
        today = datetime.date.today()
        self.model_instance = Expense.objects.create(
            name='Foobar1',
            budget=self.budget,
            category=Category.objects.create(name='cat1', budget=self.budget),
            created=datetime.date(today.year, today.month, today.day),
            updated=datetime.date(today.year, today.month, today.day),
            amount=120,
            author=self.owner,
            account=Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        )
        self.url = reverse('budgets:expense_details', kwargs={'bid': self.budget.id, 'eid': self.model_instance.id})

        self.valid_modifications = [
            {'name': 'New Name 123', 'note': 'ABC123'},

        ]
        self.invalid_modifications = [
            {'name': ''}
        ]
        self.success_message = 'EXPENSE_UPDATED'
        self.error_message = 'EXPENSE_UPDATE_FAILED'

    def test_valid_modifications_as_owner(self):
        self.check_modifications(self.valid_modifications, self.owner, self.success_message)

    def test_valid_modifications_as_rw_user(self):
        self.check_modifications(self.valid_modifications, self.owner, self.success_message)

    def test_valid_modifications_as_ro_user(self):
        self.check_modifications(self.valid_modifications, self.ro_user, 'PERMISSION_DENIED', 403)

    def test_invalid_modifications_as_owner(self):
        self.check_modifications(self.invalid_modifications, self.owner, self.error_message)

    def test_invalid_modifications_as_rw_user(self):
        self.check_modifications(self.invalid_modifications, self.rw_user, self.error_message)

    def test_invalid_modifications_as_ro_user(self):
        self.check_modifications(self.invalid_modifications, self.ro_user, 'PERMISSION_DENIED', 403)

    def test_delete_as_owner(self):
        self.check_deletion(self.url, self.owner, 200)
        self.assertEqual(0, len(type(self.model_instance).objects.filter(id=self.model_instance.id)))

    def test_delete_as_rw_user(self):
        self.check_deletion(self.url, self.rw_user, 200)
        self.assertEqual(0, len(type(self.model_instance).objects.filter(id=self.model_instance.id)))

    def test_delete_as_ro_user(self):
        self.check_deletion(self.url, self.ro_user, 403)

    def test_modification_logging(self):
        self.test_valid_modifications_as_owner()

        em_name = ExpenseModification.objects.get(field_name='name')
        self.assertEqual('Foobar1', em_name.old_value)
        self.assertEqual('New Name 123', em_name.new_value)

        em_name = ExpenseModification.objects.get(field_name='note')
        self.assertEqual('', em_name.old_value)
        self.assertEqual('ABC123', em_name.new_value)


class ExpensesTableViewTest(TestCase, BudgetSetup):
    def setUp(self):
        self.prepare_budget()
        account = Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        category = Category.objects.create(name='cat1', budget=self.budget)
        today = datetime.date.today()
        Expense.objects.create(
            name='Foobar1',
            budget=self.budget,
            category=category,
            created=today,
            updated=today,
            amount=120,
            author=self.owner,
            account=account
        )
        Expense.objects.create(
            name='Foobar2',
            budget=self.budget,
            category=category,
            created=today,
            updated=today,
            amount=130,
            author=self.owner,
            account=account
        )
        self.url = reverse('budgets:expenses_table', kwargs={'bid': self.budget.id})
        self.model_class = Expense

    def test_listing(self):
        self.client.login(username=self.owner.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        for inst in self.model_class.objects.filter(budget=self.budget):
            self.assertIn(str(inst), resp.content.decode())


class CategoryAddViewTest(WebTest, BudgetSetup, InstanceCrudSuite):
    def setUp(self):
        self.prepare_budget()
        self.url = reverse('budgets:categories_add', kwargs={'bid': self.budget.id})
        self.valid_parameters = [
            {'name': 'Category123'},
        ]
        self.invalid_parameters = [
            {'name': ''},
        ]
        self.success_message = 'CATEGORY_CREATED'
        self.error_message = 'CATEGORY_CREATION_FAILED'

    def test_valid_creations_as_owner(self):
        self.check_creation(self.valid_parameters, self.owner, None)

    def test_valid_creations_as_rw_user(self):
        self.check_creation(self.valid_parameters, self.owner, None)

    def test_invalid_creations_as_owner(self):
        self.check_creation(self.invalid_parameters, self.owner, self.error_message, 200)

    def test_invalid_creations_as_rw_user(self):
        self.check_creation(self.invalid_parameters, self.rw_user, self.error_message, 200)

    def test_creation_as_ro_user(self):
        self.client.login(username=self.ro_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)


class CategoryDetailsViewTest(WebTest, BudgetSetup, InstanceCrudSuite):
    def setUp(self):
        self.prepare_budget()
        self.model_instance = Category.objects.create(name='category1', budget=self.budget)
        self.url = reverse('budgets:category_details', kwargs={'bid': self.budget.id, 'cid': self.model_instance.id})
        self.valid_modifications = [
            {'name': 'New Name 123'},
        ]
        self.invalid_modifications = [
            {'name': ''}
        ]
        self.success_message = 'CATEGORY_UPDATED'
        self.error_message = 'CATEGORY_UPDATE_FAILED'

    def test_valid_modifications_as_owner(self):
        self.check_modifications(self.valid_modifications, self.owner, self.success_message)

    def test_valid_modifications_as_rw_user(self):
        self.check_modifications(self.valid_modifications, self.owner, self.success_message)

    def test_valid_modifications_as_ro_user(self):
        self.check_modifications(self.valid_modifications, self.ro_user, 'PERMISSION_DENIED', 403)

    def test_invalid_modifications_as_owner(self):
        self.check_modifications(self.invalid_modifications, self.owner, self.error_message)

    def test_invalid_modifications_as_rw_user(self):
        self.check_modifications(self.invalid_modifications, self.rw_user, self.error_message)

    def test_invalid_modifications_as_ro_user(self):
        self.check_modifications(self.invalid_modifications, self.ro_user, 'PERMISSION_DENIED', 403)

    def test_delete_as_owner(self):
        self.check_deletion(self.url, self.owner, 200)
        self.assertEqual(0, len(type(self.model_instance).objects.filter(id=self.model_instance.id)))

    def test_delete_as_rw_user(self):
        self.check_deletion(self.url, self.rw_user, 200)
        self.assertEqual(0, len(type(self.model_instance).objects.filter(id=self.model_instance.id)))

    def test_delete_as_ro_user(self):
        self.check_deletion(self.url, self.ro_user, 403)


class CategoriesTableViewTest(TestCase, BudgetSetup):
    def setUp(self):
        self.prepare_budget()
        Category.objects.create(name='cat1', budget=self.budget)
        Category.objects.create(name='cat2', budget=self.budget)
        self.url = reverse('budgets:categories_table', kwargs={'bid': self.budget.id})
        self.model_class = Category

    def test_listing(self):
        self.client.login(username=self.owner.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        for inst in self.model_class.objects.filter(budget=self.budget):
            self.assertIn(str(inst), resp.content.decode())


class BudgetEditView(WebTest, BudgetSetup, InstanceCrudSuite):
    def setUp(self):
        self.prepare_budget()
        self.model_instance = Budget.objects.first()
        self.url = reverse('budgets:edit', kwargs={'bid': self.budget.id})
        self.valid_modifications = [
            {'name': 'New Name 123'},
        ]
        self.invalid_modifications = [
            {'name': ''}
        ]
        self.success_message = 'BUDGET_UPDATED'
        self.error_message = 'BUDGET_UPDATE_FAILED'

    def test_valid_modifications_as_owner(self):
        self.check_modifications(self.valid_modifications, self.owner, self.success_message)

    def test_access_as_rw_user(self):
        self.client.login(username=self.rw_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)

    def test_access_as_ro_user(self):
        self.client.login(username=self.ro_user.username, password=USER_PASSWORD)
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)

    def test_invalid_modifications_as_owner(self):
        self.check_modifications(self.invalid_modifications, self.owner, self.error_message)
