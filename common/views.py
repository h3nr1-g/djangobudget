from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from budgets.models import Budget
from common.models import TranslationEntry



def common_ctx(request, budget=None):
    return {
        'my_budgets': Budget.my_budgets(request.user),
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
        query=request.GET.get('query', None)
        if not query:
            return HttpResponse('query param missing',status=400)

        try:
            return HttpResponse(TranslationEntry.objects.get(name=query).text)
        except TranslationEntry.DoesNotExist:
            return HttpResponse(f'No translation found for "{query}"',status=404)


class TranslationView(View):
    def get(self, request):
        return JsonResponse({
            te.name: te.text
            for te in TranslationEntry.objects.filter(lang=settings.LANGUAGE_CODE)
        })