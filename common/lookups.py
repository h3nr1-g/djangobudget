from ajax_select import LookupChannel


class ItemLookup(LookupChannel):
    model = None
    filter_field = None
    suffix = 'write'

    def get_query(self, q, request):
        filter_param = {f'{self.filter_field}__contains': q}
        return self.model.objects.filter(**filter_param).order_by(self.filter_field)[:50]

    def format_item_display(self, item):
        onclick = f'document.getElementById(\'kill_{item.id}id_{self.suffix}\').click()'
        return f'<div class="as-item h5">' \
               f'<button onclick="{onclick}" style="margin-left: 2px;" type="button" class="btn btn-danger btn-sm">' \
               '<i class="nav-icon fas fa-trash"></i>' \
               '</button> ' \
               f'{str(item)}' \
               f'</div>'
