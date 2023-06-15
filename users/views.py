from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse

from budgets.models import Budget
from budgets.tables import BudgetsTable
from common.models import TranslationEntry
from common.views import formpage_ctx, AuthenticatedUserView
from users.forms import PasswordChangeForm, UserDetailsForm


class PasswordChangeView(AuthenticatedUserView):
    def get(self, request):
        form = PasswordChangeForm()
        ctx = formpage_ctx(request, None, form, reverse('users:pwchange', args=(request.user.id,)))
        return render(request, 'common/formpage.html', ctx)

    def post(self, request):
        form = PasswordChangeForm(data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new'])
            request.user.save()
            messages.success(request, TranslationEntry.get('PASSWORD_UPDATED'))
        ctx = formpage_ctx(request, None, form, reverse('users:pwchange'))
        return render(request, 'common/formpage.html', ctx)


class UserDetailsView(AuthenticatedUserView):
    def get(self, request):
        ctx = self.build_ctx(request)
        return render(request, 'common/formpage_table.html', ctx)

    def build_ctx(self, request, form=None):
        used_form = form or UserDetailsForm(instance=request.user)
        return {
            'table_title': TranslationEntry.get('BUDGETS'),
            'table': BudgetsTable(Budget.objects.filter(owner=request.user)),
            **formpage_ctx(request, None, used_form, reverse('users:details'))
        }
