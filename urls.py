from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^babytimeline/', include('babytimeline.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^/?', include('babytimeline.timeline.urls')),
     (r'^contact/', include('contact_form.urls')),
     (r'^accounts/', include('registration.urls')),
     (r'^socialregistration/', include('socialregistration.urls')),
     (r'^i18n/', include('django.conf.urls.i18n')),
)

handler500 = 'timeline.views.server_error'


if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

# serve static pages when debug
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        (r'^500/$', 'timeline.views.server_error'),
    )
