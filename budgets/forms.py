from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from budgets.models import Account, Currency, Expense, Category, Budget
from common.models import TranslationEntry


class BudgetEditForm(forms.ModelForm):
    name = forms.CharField(
        label='NAME',
        initial='',
        required=True
    )
    note = forms.CharField(
        required=False,
        initial=None,
        label='NOTE',
        widget=forms.Textarea()
    )
    currency = forms.ModelChoiceField(
        Currency.objects.all(),
        empty_label=None,
        label='CURRENCY'
    )
    owner = forms.ModelChoiceField(
        User.objects.all(),
        empty_label=None,
        label='OWNER'
    )
    read_access = AutoCompleteSelectMultipleField(
        'user_read_access',
        label='READ_ACCESS',
        required=False,
    )
    write_access = AutoCompleteSelectMultipleField(
        'user_write_access',
        label='WRITE_ACCESS',
        required=False,
    )

    class Meta:
        model = Budget
        fields = ['name', 'note', 'currency', 'owner', 'read_access', 'write_access']


class AccountForm(forms.ModelForm):
    name = forms.CharField(
        label='NAME',
        initial='',
        required=True
    )
    start_balance = forms.CharField(
        label='START_BALANCE',
        initial='',
        required=True
    )
    locked = forms.BooleanField(
        label='LOCKED',
        required=False,
        initial=False,
        widget=forms.Select(choices=())
    )

    class Meta:
        model = Account
        fields = ['name', 'start_balance', 'locked']


class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        label='NAME',
        initial='',
        required=True
    )
    parent = forms.ModelChoiceField(
        Category.objects.all(),
        required=False,
        initial=None,
        label='PARENT_CATEGORY'
    )

    class Meta:
        model = Category
        fields = ['name', 'parent', ]


class ExpenseForm(forms.ModelForm):
    name = forms.CharField(
        label='NAME',
        initial='',
        required=True,
    )
    category = AutoCompleteSelectField(
        'categories',
        label='CATEGORY',
        required=True,
    )
    account = forms.ModelChoiceField(
        Account.objects.all(),
        empty_label=None,
        label='ACCOUNT'
    )
    created = forms.DateField(
        widget=DatePickerInput(),
        input_formats=settings.DATE_INPUT_FORMATS,
        label='CREATION_DATE',
        required=True,
    )
    amount = forms.FloatField(
        label='AMOUNT',
        required=True,
    )
    external_reference = forms.CharField(
        required=False,
        initial=None,
        label='EXTERNAL_REFERENCE',
    )
    note = forms.CharField(
        required=False,
        initial=None,
        label='NOTE',
        widget=forms.Textarea()
    )

    class Meta:
        model = Expense
        fields = ['name', 'account', 'category', 'amount', 'created', 'external_reference', 'note']

    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get('account')
        amount = cleaned_data.get('amount')
        created = cleaned_data.get('created')
        if account.balance_at(created) < amount:
            raise ValidationError(TranslationEntry.get('NOT_ENOUGH_MONEY'))

        return self.cleaned_data
