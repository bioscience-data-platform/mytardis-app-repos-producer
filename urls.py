from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tardis.apps.reposproducer.views',
    url(r'^user/(?P<user_id>\d+)/$', 'user'),
    url(r'^expstate/(?P<exp_id>\d+)/$', 'experiment_state'),
    url(r'^acls/(?P<exp_id>\d+)/$', 'get_acls')
)
