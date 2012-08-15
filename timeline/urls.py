# This Python file uses the following encoding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('babytimeline.timeline.views',
    (r'^$', 'index'),
    (r'^addbaby/?$', 'add_baby'),
    (r'^baby/export/(?P<baby_id>\d+).pdf/?$', 'export_baby'),
    (r'^baby/addmilestone/(?P<baby_id>\d+)/?$', 'add_milestone'),
    (r'^baby/edit/(?P<baby_id>\d+)/?$', 'edit_baby'),
    (r'^baby/delete/(?P<baby_id>\d+)/?$', 'delete_baby'),
    (r'^milestone/edit/(?P<milestone_id>\d+)/?$', 'edit_milestone'),
    (r'^milestone/delete/(?P<milestone_id>\d+)/?$', 'delete_milestone'),
    (r'^milestone/image/(?P<milestone_id>\d+)/?$', 'serve_image')
)
