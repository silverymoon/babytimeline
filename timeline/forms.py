# This Python file uses the following encoding: utf-8
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.forms.util import ErrorList

import datetime

import models

class CalendarWidget(forms.DateInput):

    def __init__(self, attrs={}, format=None):
        attrs['class'] = 'date'
        super(forms.DateInput, self).__init__(attrs)
        if format:
            self.format = format

    def render(self, name, value, attrs=None):
        value = datetime.date.today()
        return super(forms.DateInput, self).render(name, value, attrs)
        #btn = "<button id='calendar'><span class='ui-icon ui-icon-calendar'>Kalender</span></button>"
        #return mark_safe(input + btn)

    class Media:
        js = ('js/calendar.js',)

class DateTimeWidget(forms.MultiWidget):
    def __init__(self,attrs=None):
        widgets = (
            CalendarWidget(),
            forms.TextInput(attrs={'class' : 'time_input'}),
        )
        super(DateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, datetime.datetime):
                return (value.date(), value.time().strftime("%H:%M"))
            else:
                return value.split(" ")
        return (datetime.date.today(), None)

    def value_from_datadict(self, data, files, name):
        val = super(DateTimeWidget, self).value_from_datadict(data, files, name)
        return val

class MilestoneForm(forms.ModelForm):
    date = forms.DateField(label="Datum des Meilensteins",widget=CalendarWidget())
    type = forms.ChoiceField(label=u"Meilenstein auswählen...",choices = [('', '-----')]    , required=False)
    image = forms.ImageField(label="... oder Bild hochladen...", required=False)
    note = forms.CharField(label="...oder Freitext eingeben", max_length=512, required=False)
    baby = forms.CharField(widget=forms.HiddenInput())

    def translate(self, locale):
        choices = [ (fm.id, fm.get_text(locale)) for fm in models.FixedMilestone.objects.all() ]
        self.fields['type'].choices = [('', '-----')] + choices

    def clean(self):
        if 'type' in self.cleaned_data:
            self.cleanup_type()
        if 'date' in self.cleaned_data:
            self.cleanup_date()
        if self.cleaned_data['image']:
            self.cleaned_data['type'] = 'PHOTO'
        elif self.cleaned_data['note']:
            self.cleaned_data['type'] = 'FREE'
        baby_id = self.cleaned_data['baby']
        baby = models.Baby.objects.get(pk = baby_id)
        self.cleaned_data['baby'] = baby
        return self.cleaned_data

    def cleanup_type(self):
        type = self.cleaned_data['type']
        if type != 'PHOTO' and type !='FREE':
            orig_milestone = models.Milestone.objects.filter(baby = self.cleaned_data['baby'], type = type)
            if orig_milestone:
                self._errors['type'] = ErrorList(["milestone already exists!"])
                del self.cleaned_data['type']
        return type

    def cleanup_date(self):
        date = self.cleaned_data['date']
        if date.toordinal() < models.Baby.objects.get(pk = self.cleaned_data['baby']).birth_date.toordinal():
            self._errors['date'] = ErrorList(["date before baby's birth"])
            del self.cleaned_data['date']
        return date

    class Meta:
        model = models.Milestone
        fields = ['date', 'type', 'image', 'note', 'baby']


class BabyForm(forms.ModelForm):
    birth_date = forms.DateTimeField(label="Geburtsdatum und -zeit", widget=DateTimeWidget(), help_text="Zeit als hh:mm eingeben.")
    user = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = models.Baby
        fields = ['name', 'birth_date', 'weight_in_g', 'size_in_cm']

    def save(self):
        user_id = self.cleaned_data['user']
        del self.cleaned_data['user']
        baby = forms.ModelForm.save(self, commit=False)
        baby.user = User.objects.get(pk = user_id)
        baby.save()
        return baby
