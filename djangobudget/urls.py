from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from ajax_select import urls as ajax_select_urls

from budgets.views import BudgetSelectView
from users.forms import UserLoginForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ajax_select/', include(ajax_select_urls)),
    path('budgets/', include(('budgets.urls', 'budgets'))),
    path('common/', include(('common.urls', 'common'))),
    path('users/', include(('users.urls', 'users'))),
    path('', BudgetSelectView.as_view(), name='index'),
    path(
        'auth/login',
        auth_views.LoginView.as_view(template_name='users/login.html', authentication_form=UserLoginForm),
        name='login'
    ),
    path('auth/logout', auth_views.LogoutView.as_view(template_name='users/login.html'), name='logout'),
]

try:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
except Exception:
    print('Skip including of debug toolbar URLs')
