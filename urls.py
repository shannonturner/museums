from django.conf import settings
from django.conf.urls import include, url
from museums.views import HomeView

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'museums.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^(?:museums/)?admin/', include(admin.site.urls)),
    url(r'^(?:museums/)?$', HomeView.as_view(), name='home'),
]
