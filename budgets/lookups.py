from ajax_select import register, LookupChannel
from budgets.models import Category


@register('categories')
class TagsLookup(LookupChannel):
    model = Category

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:50]

    def format_item_display(self, item):
        return f'<button style="width: 95%;" type="button" class="btn btn-outline-dark">{item.name}</button>'\
               '<button onclick="deleteCategory();" style="width: 5%;" type="button" class="btn btn-danger">' \
               '<i class="nav-icon fas fa-trash"></i>' \
               '</button>'
