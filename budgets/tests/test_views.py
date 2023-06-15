import json
from datetime import datetime as dt

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django_webtest import WebTest

from budgets.models import Budget, Account, Expense, Currency


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
        self.budget.owner = self.test_user
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


class AccountsDetailsView(WebTest):
    def setUp(self):
        self.budget = Budget.objects.create(name='budget1', currency=Currency.objects.create(name='Dollar', symbol='$'))
        self.test_user = User.objects.create_user(username='user1', password='12345')
        self.budget.owner = self.test_user
        self.budget.save()
        self.account = Account.objects.create(budget=self.budget, name='account1', start_balance=1000)
        self.url = reverse('budgets:account_details', kwargs={'bid': self.budget.id, 'aid': self.account.id})

    def test_read_as_owner(self):
        resp = self.app.get(self.url, user=self.test_user)
        self.assertEqual(200, resp.status_code)
