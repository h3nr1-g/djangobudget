from ajax_select import register, LookupChannel
from budgets.models import Category


@register('categories')
class TagsLookup(LookupChannel):
    model = Category

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:50]

    def format_item_display(self, item):
        return f'<button class="btn btn-primary w-100">{item.name}</button>'
