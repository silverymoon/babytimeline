# This Python file uses the following encoding: utf-8
from django.views.generic import simple,list_detail, create_update
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import Context, loader
from django.utils.translation import ugettext as _

from functools import wraps
import locale

import models
import forms
import export

def permission(permission_tester):
    @wraps(permission_tester)
    def view_decorator(view_function):
        @wraps(view_decorator)
        def decorated_view(request, *args, **kwargs):
            if permission_tester(request, *args, **kwargs):
                view_result = view_function(request, *args, **kwargs)
            else:
                view_result = simple.direct_to_template(request, 'timeline/not_allowed.html',)
            return view_result
        return decorated_view
    return view_decorator

@permission
def user_owns_baby(request, baby_id):
    return request.user == models.Baby.objects.get(pk = baby_id).user

@permission
def user_owns_milestone(request, milestone_id):
    return request.user == models.Milestone.objects.get(pk = milestone_id).baby.user

INDEX_PAGE = "/"

def fix_form(request, field, form, data, instance=None):
    hash = request.POST.copy()
    hash[field] = data
    return form(hash, request.FILES, instance=instance)

def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL
    })))


@login_required
def index(request):
    return list_detail.object_list(request,
                                   models.Baby.objects.filter(user = request.user),
                                   template_name = 'timeline/index.html',
                                   template_object_name = "baby",
                                   extra_context = {"title" : _("Willkommen bei Babytimeline")})

@login_required
def add_baby(request):
    if request.method == 'POST':
        form = fix_form(request, 'user', forms.BabyForm, request.user.id)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(INDEX_PAGE)
    else:
        form = forms.BabyForm(initial = {'user' : request.user.id})
    return simple.direct_to_template(request, 'timeline/baby_form.html',
                                       extra_context = {"form": form,
                                                        "title" : _(u"Baby hinzufügen"),
                                                        "action": "/addbaby/"})


@login_required
@user_owns_baby
def edit_baby(request, baby_id):
    baby = models.Baby.objects.get(pk = baby_id)
    if request.method == 'POST':
        form = fix_form(request, 'user', forms.BabyForm, request.user.id, instance=baby)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(INDEX_PAGE)
    else:
        form = forms.BabyForm(instance=baby)
    return simple.direct_to_template(request, 'timeline/baby_form.html',
                                            extra_context = {"form": form,
                                                        "object": baby,
                                                        "title" : _("Baby editieren"),
                                                        "action": "/baby/edit/%s" %baby_id})

@login_required
@user_owns_baby
def delete_baby(request, baby_id):
    return create_update.delete_object(request,
                                       object_id = baby_id,
                                       model = models.Baby,
                                       extra_context = {"title" : _(u"Baby löschen"),
                                                        "action": "/baby/delete/%s" %baby_id},
                                       post_delete_redirect = INDEX_PAGE)


@login_required
@user_owns_milestone
def delete_milestone(request, milestone_id):
    return create_update.delete_object(request,
                                       object_id = milestone_id,
                                       model = models.Milestone,
                                       extra_context = {"title" : _(u"Meilenstein löschen"),
                                                        "action": "/milestone/delete/%s" %milestone_id},
                                       post_delete_redirect = INDEX_PAGE)

@login_required
@user_owns_milestone
def edit_milestone(request, milestone_id):
    milestone = models.Milestone.objects.get(pk = milestone_id)
    if request.method == 'POST':
        form = fix_form(request, 'baby', forms.MilestoneForm, milestone.baby.id, instance=milestone)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(INDEX_PAGE)
    else:
        form = forms.MilestoneForm(instance=milestone)
    form.translate(request.LANGUAGE_CODE)
    return simple.direct_to_template(request, 'timeline/milestone_form.html',
                              extra_context={'form': form,
                                             'object': milestone,
                                             'title': _("Meilenstein editieren"),
                                             'action': "/milestone/edit/%s" %milestone_id})

@login_required
@user_owns_baby
def add_milestone(request, baby_id):
    if request.method == 'POST':
        form = fix_form(request, 'baby', forms.MilestoneForm, baby_id)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(INDEX_PAGE)
    else:
        form = forms.MilestoneForm(initial = {'baby' : baby_id})
    form.translate(request.LANGUAGE_CODE)
    return simple.direct_to_template(request, 'timeline/milestone_form.html',
                              extra_context={'form': form,
                                             'title': _(u"Meilenstein hinzufügen"),
                                             'baby_id' : baby_id,
                                             'action': "/baby/addmilestone/%s" %baby_id})

@login_required
@user_owns_milestone
def serve_image(request, milestone_id):
    ms = models.Milestone.objects.get(pk=milestone_id)
    fname = ms.image.path
    return download_file(fname, ms.image.name, "application/image")

def download_file(path, name, type, file=False):
    file = open(path)
    fcont = ""
    for line in file:
        fcont += line
    response = HttpResponse(fcont, mimetype=type)
    if file:
        response['Content-Disposition'] = 'attachment; filename=%s' %name
    return response

@login_required
@user_owns_baby
def export_baby(request, baby_id):
    conf = export.ExportConfig(locale = request.LANGUAGE_CODE)
    pdf = export.Exporter(export.CairoPDFDrawEngine(conf), export.ConstraintPosFactory(conf.dim), conf)
    prefix = settings.USER_FILES + "/exports/"
    baby = models.Baby.objects.get(pk=baby_id)
    fname = pdf.export(baby, prefix, "")
    return download_file(fname, fname, "application/pdf", True)