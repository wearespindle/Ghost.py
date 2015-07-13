from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    (r'^$', include('example.app.urls')),
    url(
        regex=r'^login/$',
        view='django.contrib.auth.views.login',
        kwargs={'template_name': 'accounts/login.html'},
        name='login'
    ),
    url(
        regex=r'^logout/$',
        view='django.contrib.auth.views.logout',
        kwargs={'next_page': '/'},
        name='logout'
    ),
)
