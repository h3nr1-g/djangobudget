from django.contrib.auth.models import User
from django.urls import reverse
from django_webtest import WebTest

from budgets.models import Budget
from budgets.tests import fixtures as budget_fixtures
from users.tests import fixtures as user_fixtures


class DashboardViewTest(WebTest):
    def setUp(self):
        budget_fixtures.create_currencies()
        budget_fixtures.create_budgets()
        user_fixtures.create_users()
        self.budget = Budget.objects.first()
        self.test_user = User.objects.first()

    def test_dashboard_access_as_anonymous(self):
        resp = self.client.get(reverse('budgets:dashboard',kwargs={'bid':self.budget.id}))
        self.assertEqual(302, resp.status_code)
        self.assertIn('/auth/login',resp.headers.get('location'))