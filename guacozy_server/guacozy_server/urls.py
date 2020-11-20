"""guacozy_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from users.views import CustomLoginView

# Hide "View Site" link, because admin will be often used in IFRAME
admin.site.site_url = None

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('backend.api.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='/cozy/')),
]

if settings.OKTA_AUTH is not None:
    # Okta auth
    urlpatterns.append(path('accounts/', include(("okta_oauth2.urls", "okta_oauth2"), namespace="okta_oauth2")))
elif settings.SAML2_AUTH is not None:
    import django_saml2_auth.views
    urlpatterns.append(path('saml2_auth/', include('django_saml2_auth.urls')))
    urlpatterns.append(path('accounts/login/', django_saml2_auth.views.signin))
    urlpatterns.append(path('admin/login/', django_saml2_auth.views.signin))
else:
    # Normal or LDAP auth
    urlpatterns.append(path('accounts/login/', CustomLoginView.as_view(), name='login'))
    urlpatterns.append(path('accounts/logout/', LogoutView.as_view(), name='logout'))

