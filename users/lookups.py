from ajax_select import register
from django.contrib.auth.models import User

from common.lookups import ItemLookup


@register('user_read_access')
class UserReadAccessLookup(ItemLookup):
    model = User
    filter_field = 'username'
    suffix = 'read_access'


@register('user_write_access')
class UserWriteAccessLookup(ItemLookup):
    model = User
    filter_field = 'username'
    suffix = 'write_access'
