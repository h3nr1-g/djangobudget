from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from budgets.models import Budget
from common.models import TranslationEntry


def common_ctx(request, budget=None):
    if request.user.is_superuser:
        budgets = Budget.objects.all()
    else:
        budgets = set(Budget.objects.filter(Q(read_access__in=[request.user]) | Q(owner=request.user)))

    return {
        'my_budgets': budgets,
        'budget': budget
    }


def formpage_ctx(request, budget, form, form_url):
    return {
        **common_ctx(request, budget),
        'form': form,
        'url': form_url,
    }


class AuthenticatedUserView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthenticatedUserView, self).dispatch(request, *args, **kwargs)


class TranslateItemView(View):
    def get(self, request):
        query = request.GET.get('query', None)
        if not query:
            return HttpResponse('query param missing', status=400)

        try:
            return HttpResponse(TranslationEntry.objects.get(name=query).text)
        except TranslationEntry.DoesNotExist:
            return HttpResponse(f'No translation found for "{query}"', status=404)


class TranslationView(View):
    def get(self, request):
        return JsonResponse({
            te.name: te.text
            for te in TranslationEntry.objects.filter(lang=settings.LANGUAGE_CODE)
        })


def error_403(request, exception):
    resp = render(request, 'common/errors/403.html')
    resp.status_code = 403
    return resp


def error_404(request, exception):
    resp = render(request, 'common/errors/404.html')
    resp.status_code = 404
    return resp


def error_500(request):
    resp = render(request, 'common/errors/500.html')
    resp.status_code = 500
    return resp
