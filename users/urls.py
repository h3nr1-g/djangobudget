from django.urls import path

from users.views import PasswordChangeView, UserDetailsView

urlpatterns = [
    path('pwchange', PasswordChangeView.as_view(), name='pwchange'),
    path('details', UserDetailsView.as_view(), name='details'),
]
