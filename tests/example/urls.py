from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    (r'^$', include('example.app.urls')),
)
