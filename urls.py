from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tardis.apps.reposproducer.views',
    url(r'^user/(?P<user_id>\d+)/$', 'user'),
)