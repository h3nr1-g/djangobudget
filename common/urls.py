from django.urls import path

from common.views import TranslateItemView,TranslationView

urlpatterns = [
    path('translate/item', TranslateItemView.as_view(), name='translate'),
    path('translate/all', TranslationView.as_view(), name='translation'),
]
