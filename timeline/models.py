# This Python file uses the following encoding: utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.utils import translation

import Image
import os.path

fpath = settings.USER_FILES + '/uploads/baby_photos/'
storage = FileSystemStorage(location=fpath, base_url="")

def uploader(instance, fname):
    return "%d_%s" %(instance.baby.user.id, fname)

class Baby(models.Model):
    birth_date = models.DateTimeField()
    weight_in_g = models.IntegerField("Gewicht in Gramm")
    size_in_cm = models.IntegerField("Größe in cm")
    name = models.CharField("Name", max_length=64)
    user = models.ForeignKey(User)

    def birth_data(self):
        return "%s: %dg, %dcm" %(self.birth_date.strftime("%x"), self.weight_in_g, self.size_in_cm)

    def __unicode__(self):
        return self.name

    def idstr(self):
        return str(self.id)

    def get_sorted_milestones(self):
        milestones = list(self.milestone_set.all())
        milestones.sort(lambda a, b: cmp(a.date.toordinal(), b.date.toordinal()))
        return milestones

    def pdfurl(self):
        return "/baby/export/%d.pdf" % self.id

class FixedMilestone(models.Model):
    type = models.CharField(max_length=8, blank=False, unique=True)
    text = models.CharField(max_length=512, blank=True)
    text_en = models.CharField(max_length=512, blank=True, null=True)

    def get_text(self, locale):
        if locale == "en":
            return self.text_en
        return self.text

    def __unicode__(self):
        return self.type

class Milestone(models.Model):
    TYPE_CHOICES =(
        (u'BIRTH', 'Geburt'),
        (u'FREE', 'Freitext'),
        (u'PHOTO', 'Photo'),
        (u'FIXED', 'Fix')
    )
    date = models.DateField()
    note = models.CharField("Freitext", max_length=512, blank=True)
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    fixed = models.ForeignKey(FixedMilestone, null=True)
    image = models.ImageField("Bild", upload_to=uploader, storage=storage, blank=True)
    baby = models.ForeignKey(Baby)

    def get_text(self, locale=translation.get_language()):
        if not self.is_photo():
            if self.type == "FREE" or self.type == "BIRTH":
                return self.note
            return self.fixed.get_text(locale)
        return ""

    def idstr(self):
        return str(self.id)

    def get_text_date(self, locale=translation.get_language()):
        if not self.is_photo():
            text = ""
            if self.type != "BIRTH":
                text = self.date.strftime("%d.: ")
            return text + self.get_text(locale)
        return ""

    def resize_height(self, height):
        if self.is_photo():
            width = height / self.image.height * self.image.width
            return (width, height)
        return False

    def is_photo(self):
        return self.type == 'PHOTO'

    def get_png_file(self):
        if self.is_photo():
            fname = self.image.path
            if not fname.endswith(".png"):
                png = fname + ".png"
                if not os.path.isfile(png):
                    im = Image.open(fname)
                    if im.format != "PNG":
                        im.save(png)
                return png
            return fname
        return ""

    def __unicode__(self):
        return self.date.strftime("%d.%m.") + " " + self.get_text()
