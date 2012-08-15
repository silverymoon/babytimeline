# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        import timeline.models
        MILESTONE_CHOICES = (
        (u'SMILE', u'ich lächele!'),
        (u'SLEEP', u'ich schlafe länger als 6 Stunden'),
        (u'ROLL', u'ich drehe mich auf den Rücken'),
        (u'LAUGH', u'ich kann lachen'),
        (u'GRAB', u'ich greife'),
        (u'EATS', u'ich darf was essen'),
        (u'CRAWL', u'ich kann krabbeln!'),
        (u'SIT', u'ich kann sitzen'),
        (u'STAND', u'ich kann aufstehen'),
        (u'PINCER', u'ich greife mit Pinzettengriff'),
        (u'GUGU', u'ich spiele Kuckuck!'),
        (u'WALK', u'ich kann laufen!')
        )
        for mc in MILESTONE_CHOICES:
            if not orm.FixedMilestone.objects.filter(type = mc[0]):
                fm = timeline.models.FixedMilestone(type = mc[0], text = mc[1])
                fm.save()
        for ms in orm.Milestone.objects.all():
            if ms.type != 'PHOTO' and ms.type != 'FREE' and ms.type != 'FIXED':
                fm = orm.FixedMilestone.objects.get(type = ms.type)
                ms.fixed = fm
                ms.type = "FIXED"
                ms.save()

    def backwards(self, orm):
        for ms in orm.Milestone.objects.all():
            if ms.type == "FIXED":
                fm = ms.fixed
                ms.type = fm.type
                ms.save()

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'timeline.baby': {
            'Meta': {'object_name': 'Baby'},
            'birth_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'size_in_cm': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight_in_g': ('django.db.models.fields.IntegerField', [], {})
        },
        'timeline.fixedmilestone': {
            'Meta': {'object_name': 'FixedMilestone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'timeline.milestone': {
            'Meta': {'object_name': 'Milestone'},
            'baby': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeline.Baby']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'fixed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeline.FixedMilestone']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        }
    }

    complete_apps = ['timeline']
