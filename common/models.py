from django.conf import settings
from django.db import models

CHARFIELD_PARAMS = {
    'max_length': 100,
}

NOT_NULLABLE = {
    'null': False,
    'blank': False,
}

NULLABLE = {
    'null': True,
    'blank': True,
}

UNIQUE_CHARFIELD = {
    **CHARFIELD_PARAMS,
    **NOT_NULLABLE,
    'unique': True
}


class TranslationEntry(models.Model):
    name = models.CharField(
        **CHARFIELD_PARAMS,
        default='',
    )
    text = models.CharField(
        **CHARFIELD_PARAMS,
        default='',
    )
    lang = models.CharField(
        **CHARFIELD_PARAMS,
        default='de',
        null=True
    )

    class Meta:
        unique_together =('name', 'lang')

    def __str__(self):
        return f'{self.name} ({self.lang})'

    @staticmethod
    def get(name, alt_lang=None):
        lang = alt_lang or settings.LANGUAGE_CODE
        return TranslationEntry.objects.get(name=name, lang=lang).text
