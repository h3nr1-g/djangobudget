from django.contrib import admin
from common.models import TranslationEntry


class TranslationEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'lang')


# Register your models here.
admin.site.register(TranslationEntry, TranslationEntryAdmin)
