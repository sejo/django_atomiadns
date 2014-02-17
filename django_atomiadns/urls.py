from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'django_atomiadns.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),

                       url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}),
                       url(r'^about/?$', TemplateView.as_view(template_name='about.html')),
                       url(r'^change_password/?$', 'web.views.change_password'),

                       # main page
                       url(r'^/?(?P<offset>\d+)?/?$', 'web.views.home'),

                       # login
                       url(r'^login/?$', 'web.views.login'),

                       # edit zone
                       url(r'^edit/(?P<zone>[^/]+)/?', 'web.views.edit'),
                       # export zone
                       url(r'^export/(?P<zone>[^/]+)/?', 'web.views.export'),

                       # import zone
                       url(r'^import/(?P<zone>[^/]+)/?', 'web.views.import_zone'),


                       # ajax calls zone

                       url(r'^ajax/add_zone/?$', 'web.post.add_zone'),
                       url(r'^ajax/remove_zone/?$', 'web.post.remove_zone'),
                       url(r'^ajax/import_zone/?', 'web.post.import_zone'),
                       # ajax calls record
                       url(r'^ajax/change_record/?$', 'web.post.change_record'),
                       url(r'^ajax/add_record/?$', 'web.post.add_record'),
                       url(r'^ajax/remove_record/?$', 'web.post.remove_record'),
)
