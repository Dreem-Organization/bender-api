"""bender URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from bender_service.social_login import FacebookLogin, GoogleLogin
from django.views.generic import TemplateView
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Rest auth (login signup etc.)
    url(r'^', include('rest_auth.urls')),

    # This is not meant to be used, it just allows allauth to send email of reset
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        TemplateView.as_view(),
        name='password_reset_confirm'),  # https://github.com/Tivix/django-rest-auth/issues/63

    # Registration
    url(r'^registration/', include('rest_auth.registration.urls')),
    url(r'^facebook/', FacebookLogin.as_view(), name='facebook_login'),
    url(r'^google/', GoogleLogin.as_view(), name='google_login'),

    # Necessary imports (profile seems useless for now.)
    url(r'^accounts/profile/$',
        RedirectView.as_view(url='/', permanent=True),
        name='profile-redirect'),
    url(r'^account/', include('allauth.urls')),

    # Bender import
    url(r'^api/', include('bender.urls')),
]
