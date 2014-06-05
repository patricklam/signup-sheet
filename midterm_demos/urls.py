from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'midterm_demos.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^signup/', include('signup.urls', namespace="signup")),
    url(r'^admin/', include(admin.site.urls)),
)
