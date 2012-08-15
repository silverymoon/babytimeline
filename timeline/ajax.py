# This Python file uses the following encoding: utf-8
from django.utils import simplejson
from django.template import RequestContext
from django.template.loader import render_to_string
from dajax.core import Dajax
import models
import forms

def timeline_details(request, tl_id):
    tl = models.Timeline.objects.get(pk=tl_id)
    dajax = Dajax()
    context = RequestContext(request)
    dajax.append("#accordion", "innerHTML", tl.baby.to_html(context))
    milestones = [ms.to_html(context) for ms in tl.get_sorted_milestones()]
    dajax.append("#babydetails_" + str(tl_id), "innerHTML", "\n".join(milestones))
    dajax.addData("", "load_finished")
    return dajax.json()
    
def show_photo_editor(request):
    dajax = Dajax()
    context = RequestContext(request)
    dict = {"title": "Photo hinzufügen",
            "name": "add_photo",
            "id": "add_photo",
            "form": forms.PhotoForm()
    }
    form = render_to_string("timeline/photo_editor.html", dict, context)
    dajax.addData(form, "show_editor")
    return dajax.json()
  
def add_timeline(request):
    pass

def add_event(request, baby_id):
    pass

def add_photo(request, baby_id):
    pass

def delete_timeline(request, timeline_id):
    pass

def delete_event(request, event_id):
    pass

def delete_photo(request, photo_id):
    pass

def update_baby(request, baby_id):
    pass

def update_event(request, event_id):
    pass

def update_photo(request, photo_id):
    pass
