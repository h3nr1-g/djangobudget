from ajax_select import register
from budgets.models import Category
from common.lookups import ItemLookup


@register('categories')
class CategoryLookup(ItemLookup):
    model = Category
    filter_field = 'name'
    suffix = 'category'

    def format_item_display(self, item):
        onclick = f'document.getElementById(\'kill_{item.id}id_{self.suffix}\').click()'
        return f'<button type="button" class="as-item btn btn-outline-dark w-50">{str(item)}</button>' \
               f'<button onclick="{onclick}" style="margin-left: 2px;" type="button" class="btn btn-danger">' \
               '<i class="nav-icon fas fa-trash"></i>' \
               '</button>'
