import datetime
import json
from datetime import datetime as dt

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django_webtest import WebTest

from budgets.models import Budget, Account, Expense, Currency, Category, ExpenseModification


class BudgetSelectView(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.budget1 = Budget.objects.create(name='budget1')
        self.budget2 = Budget.objects.create(name='budget2', note='XXXXX')
        self.url = reverse('index')

    def test_access_as_anonymous_user(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
        self.assertIn('/auth/login', resp.headers.get('location'))

    def test_access_as_unrelated_user(self):
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertNotIn(self.budget1.name, resp.content.decode())
        self.assertNotIn(self.budget2.name, resp.content.decode())

    def test_as_budget_owner(self):
        self.budget2.owner = self.test_user
        self.budget2.save()
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertNotIn(self.budget1.name, resp.content.decode())
        self.assertIn(self.budget2.name, resp.content.decode())
        self.assertIn(self.budget2.note, resp.content.decode())

    def test_as_ro_user(self):
        self.budget2.read_access.add(self.test_user)
        self.budget2.save()
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertNotIn(self.budget1.name, resp.content.decode())
        self.assertIn(self.budget2.name, resp.content.decode())
        self.assertIn(self.budget2.note, resp.content.decode())


class DashboardViewTest(TestCase):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1')
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.url = reverse('budgets:dashboard', kwargs={'bid': self.budget.id})

    def test_access_as_anonymous_user(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
        self.assertIn('/auth/login', resp.headers.get('location'))

    def test_access_as_unauthorized_user(self):
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)

    def test_access_as_owner(self):
        self.budget.owner = self.test_user
        self.budget.save()
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertIn(self.budget.name, resp.content.decode())

    def test_as_ro_user(self):
        self.budget.read_access.add(self.test_user)
        self.budget.save()
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertIn(self.budget.name, resp.content.decode())


class DashboardDataView(TestCase):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1')
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.url = reverse('budgets:dashboard_data', kwargs={'bid': self.budget.id})

    def test_access_as_anonymous_user(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
        self.assertIn('/auth/login', resp.headers.get('location'))

    def test_access_as_unauthorized_user(self):
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)

    def test_access_as_owner(self):
        self.budget.owner = self.test_user
        self.budget.save()
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)

    def test_as_ro_user(self):
        self.budget.read_access.add(self.test_user)
        self.budget.save()
        self.client.login(username=self.test_user.username, password='12345')
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
        self.assertEqual('400,00', stats['expenses'])
        self.assertEqual('600,00', stats['remaining_budget'])
        self.assertEqual('1000,00', stats['total_budget'])
        self.assertEqual(2, stats['num_accounts'])

        self.assertIn('charts', data)
        charts = data.get('charts')
        self.assertIn('series', charts['history'])
        self.assertIn('series', charts['history'])


class AccountAddViewTest(WebTest):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1', currency=Currency.objects.create(name='Dollar', symbol='$'))
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.test_user2 = User.objects.create_user(username='user2', password='12345')
        self.budget.owner = self.test_user
        self.budget.read_access.add(self.test_user2)
        self.budget.save()
        self.url = reverse('budgets:accounts_add', kwargs={'bid': self.budget.id})

    def test_successful_add(self):
        resp = self.app.get(self.url, user=self.test_user)
        self.assertEqual(200, resp.status_code)
        form = resp.form
        form['name'] = 'Account1'
        form['start_balance'] = 5000
        resp = form.submit()
        self.assertEqual(302, resp.status_code)
        self.assertEqual('/budgets/1/accounts/1', resp.headers['Location'])
        acc = Account.objects.filter(name='Account1', start_balance=5000, budget=self.budget)
        self.assertEqual(1, len(acc))

    def test_dup_same_budget(self):
        a_org = Account.objects.create(name='Account1', budget=self.budget)
        resp = self.app.get(self.url, user=self.test_user)
        self.assertEqual(200, resp.status_code)
        form = resp.form
        form['name'] = a_org.name
        form['start_balance'] = 5000
        resp = form.submit()
        self.assertEqual(200, resp.status_code)
        self.assertIn('NAME_ALREADY_IN_USE', resp.content.decode())
        self.assertEqual(1, len(Account.objects.filter(name=a_org.name, budget=a_org.budget)))

    def test_invalid_data(self):
        resp = self.app.get(self.url, user=self.test_user)
        self.assertEqual(200, resp.status_code)
        form = resp.form
        resp = form.submit()
        self.assertEqual(200, resp.status_code)
        self.assertIn('ACCOUNT_CREATION_FAILED', resp.content.decode())
        self.assertEqual(0, len(Account.objects.all()))

    def test_creation_as_ro_user(self):
        resp = self.app.get(self.url, user=self.test_user2, status='*')
        self.assertEqual(403, resp.status_code)


class AccountsDetailsView(WebTest):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1', currency=Currency.objects.create(name='Dollar', symbol='$'))
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.test_user2 = User.objects.create_user(username='user2', password='12345')
        self.budget.owner = self.test_user
        self.budget.read_access.add(self.test_user2)
        self.budget.write_access.add(self.test_user2)
        self.budget.save()
        self.account = Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        self.account2 = Account.objects.create(budget=self.budget, name='account2', start_balance=1000)
        self.url = reverse('budgets:account_details', kwargs={'bid': self.budget.id, 'aid': self.account.id})

    def test_edit_as_owner(self):
        resp = self.app.get(self.url, user=self.test_user)
        self.assertEqual(200, resp.status_code)
        form = resp.form
        form['name'] = 'DEF567'
        resp = form.submit()
        self.assertEqual(200, resp.status_code)
        self.assertIn('ACCOUNT_UPDATED', resp.content.decode())
        self.assertEqual(1, len(Account.objects.filter(name='DEF567', budget=self.budget)))

    def test_edit_as_ro_user(self):
        self.budget.write_access.remove(self.test_user2)
        self.budget.save()
        resp = self.app.get(self.url, user=self.test_user2)
        self.assertEqual(200, resp.status_code)
        form = resp.form
        form['name'] = 'DEF567'
        resp = form.submit(status='*')
        self.assertEqual(403, resp.status_code)

    def test_name_duplicate(self):
        resp = self.app.get(self.url, user=self.test_user)
        self.assertEqual(200, resp.status_code)
        form = resp.form
        form['name'] = self.account2.name
        resp = form.submit()
        self.assertEqual(200, resp.status_code)
        self.assertIn('ACCOUNT_UPDATE_FAILED', resp.content.decode())

    def test_delete_as_owner(self):
        self.assertEqual(1, len(Account.objects.filter(id=self.account.id)))
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.delete(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(0, len(Account.objects.filter(id=self.account.id)))

    def test_delete_as_authorized_user(self):
        self.assertEqual(1, len(Account.objects.filter(id=self.account.id)))
        self.client.login(username=self.test_user2.username, password='12345')
        resp = self.client.delete(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(0, len(Account.objects.filter(id=self.account.id)))

    def test_delete_as_ro_user(self):
        self.assertEqual(1, len(Account.objects.filter(id=self.account.id)))
        self.budget.write_access.remove(self.test_user2)
        self.budget.save()
        self.client.login(username=self.test_user2.username, password='12345')
        resp = self.client.delete(self.url)
        self.assertEqual(403, resp.status_code)
        self.assertEqual(1, len(Account.objects.filter(id=self.account.id)))


class AccountsTableView(TestCase):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1', currency=Currency.objects.create(name='Dollar', symbol='$'))
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.budget.owner = self.test_user
        self.budget.save()
        self.account = Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        self.account2 = Account.objects.create(budget=self.budget, name='account2', start_balance=1000)
        self.url = reverse('budgets:accounts_table', kwargs={'bid': self.budget.id})

    def test_listing(self):
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        for a in Account.objects.filter(budget=self.budget):
            self.assertIn(a.name, resp.content.decode())


class ExpenseDetailsView(WebTest):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1', currency=Currency.objects.create(name='Dollar', symbol='$'))
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.test_user2 = User.objects.create_user(username='user2', password='12345')
        self.budget.owner = self.test_user
        self.budget.read_access.add(self.test_user2)
        self.budget.write_access.add(self.test_user2)
        self.budget.save()
        self.account = Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        self.category = Category.objects.create(name='cat1', budget=self.budget)
        today = datetime.date.today()
        self.expense = Expense.objects.create(
            name='Foobar1',
            budget=self.budget,
            category=self.category,
            created=datetime.date(today.year, today.month, today.day),
            updated=datetime.date(today.year, today.month, today.day),
            amount=120,
            author=self.test_user,
            account=self.account
        )
        self.url = reverse('budgets:expense_details', kwargs={'bid': self.budget.id, 'eid': self.expense.id})

    def test_mod_as_owner(self):
        old_id = Expense.objects.get(name='Foobar1').id
        resp = self.app.get(self.url, user=self.test_user)
        self.assertEqual(200, resp.status_code)
        form = resp.form
        form['name'] = 'ABC123'
        form['note'] = 'Hello World'
        resp = form.submit()
        self.assertEqual(200, resp.status_code)
        self.assertIn('EXPENSE_UPDATED', resp.content.decode())
        exp = Expense.objects.get(name='ABC123')
        self.assertEqual(old_id, exp.id)
        self.assertEqual('Hello World', exp.note)

    def test_modification_logging(self):
        self.assertEqual(0, len(ExpenseModification.objects.filter(expense=self.expense)))
        self.test_mod_as_owner()

        em_name = ExpenseModification.objects.get(expense=self.expense, field_name='name')
        self.assertEqual('Foobar1', em_name.old_value)
        self.assertEqual('ABC123', em_name.new_value)

        em_note = ExpenseModification.objects.get(expense=self.expense, field_name='note')
        self.assertEqual('', em_note.old_value)
        self.assertEqual('Hello World', em_note.new_value)


class ExpensesTableViewTest(TestCase):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1', currency=Currency.objects.create(name='Dollar', symbol='$'))
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.budget.owner = self.test_user
        self.budget.save()
        self.account = Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        self.category = Category.objects.create(name='cat1', budget=self.budget)
        today = datetime.date.today()
        Expense.objects.create(
            name='Foobar1',
            budget=self.budget,
            category=self.category,
            created=datetime.date(today.year, today.month, today.day),
            updated=datetime.date(today.year, today.month, today.day),
            amount=120,
            author=self.test_user,
            account=self.account
        )
        Expense.objects.create(
            name='Foobar2',
            budget=self.budget,
            category=self.category,
            created=datetime.date(today.year, today.month, today.day),
            updated=datetime.date(today.year, today.month, today.day),
            amount=130,
            author=self.test_user,
            account=self.account
        )
        self.url = reverse('budgets:expenses_table', kwargs={'bid': self.budget.id})

    def test_get_as_owner(self):
        self.client.login(username=self.test_user.username, password='12345')
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
