from django.test import TestCase
import models, export, forms
from views import user_owns_baby, user_owns_milestone
import locale
import datetime
import Image
import mox
from django.contrib.auth.models import User
from nose.plugins.attrib import attr


class ModelTest(TestCase):
    fixtures = ['test_data.json']

    def test_event(self):
        e = models.Milestone.objects.get(pk=2)
        assert not e.is_photo()
        assert e.get_text_date() == "13.: ich darf was essen"
        e = models.Milestone.objects.get(pk=18)
        assert e.get_text() == "foobarbaz"

    def test_baby(self):
        b = models.Baby.objects.get(pk=2)
        assert b.birth_data() == "11/11/01: 4567g, 45cm"
        assert b.get_sorted_milestones() == [models.Milestone.objects.get(pk=18), models.Milestone.objects.get(pk=17)]

    def test_photo(self):
        p = models.Milestone.objects.get(pk=17)
        assert p.is_photo()
        assert p.resize_height(40.0)[0] == 32
        assert not p.get_text()
        assert not p.get_text_date()
        f = p.get_png_file()
        im = Image.open(f)
        assert im.format == "PNG"

class ViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.user = User.objects.get(pk=6)
        self.success = "SUCCESS!!"

    @user_owns_baby
    def t1(request, baby_id):
        return request.success

    @user_owns_milestone
    def t2(request, milestone_id):
        return request.success

    def test_decorators(self):
        assert self.t1(2) == self.success
        assert self.t1(1) != self.success
        assert self.t2(18) == self.success
        assert self.t2(10) != self.success

class ExportTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        conf = export.ExportConfig()
        self.mox = mox.Mox()
        self.baby = models.Baby.objects.get(pk = 2)
        self.milestones = models.Baby.objects.get(pk = 1).get_sorted_milestones()
        self.drawmock = self.mox.CreateMock(export.CairoPDFDrawEngine)
        self.exp = export.Exporter(self.drawmock, export.SimplePosFactory(conf.dim), conf)
        self.d1 = datetime.date(2008, 1, 1)
        self.d2 = datetime.date(2008, 8, 1)

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_create_ticks(self):
        ticks = self.exp.create_ticks(self.d2, 1, 11)
        assert len(ticks.keys()) == 11
        assert ticks[31] == u'August'
        assert ticks[62] == u'September'
        assert ticks[92] == u'October'
        assert ticks[123] == u'November'
        assert ticks[153] == u'December'
        assert ticks[184] == u'January'
        assert ticks[215] == u'February'
        assert ticks[243] == u'March'
        assert ticks[274] == u'April'
        assert ticks[304] == u'May'
        assert ticks[335] == u'June'

    def test_calculate_month_length(self):
        assert 30 == self.exp.calculate_month_length(1976, 11, 1)
        assert 2.9 == self.exp.calculate_month_length(2004, 2, 10.0)

    def test_calculate_last_tick(self):
        assert self.exp.calculate_last_tick(self.d2, 100.0) == 0.31
        assert self.exp.calculate_last_tick(self.d1, 10.0) == 3.1

    def test_filter_milestones(self):
        list = self.exp.filter_milestones_delta(self.milestones, datetime.date(2009, 8, 25), datetime.timedelta(31))
        assert list[0].id == 15
        assert list[1].id == 6
        assert list[2].id == 7

    def test_export_year(self):
        self.drawmock.draw_background()
        self.drawmock.draw_axis(mox.IgnoreArg())
        self.drawmock.draw_photo(mox.IsA(export.Position))
        self.drawmock.finish_page()
        self.mox.ReplayAll()
        self.exp.export_year(self.baby, datetime.date(2002, 8, 1), self.baby.get_sorted_milestones()[1:])
        self.mox.VerifyAll()

    def test_export_complete(self):
        mocktoday = datetime.date(2003, 1, 1)
        self.drawmock.prepare_export("Foobar", "", "")
        self.drawmock.draw_background()
        self.drawmock.draw_axis(mox.IgnoreArg())
        self.drawmock.draw_event(mox.IsA(export.Position))
        self.drawmock.draw_event(mox.IsA(export.Position))
        self.drawmock.finish_page()
        self.drawmock.draw_background()
        self.drawmock.draw_axis(mox.IgnoreArg())
        self.drawmock.draw_photo(mox.IsA(export.Position))
        self.drawmock.finish_page()
        self.drawmock.save_file().AndReturn("Foobar.pdf")
        self.mox.ReplayAll()
        assert self.exp.export(self.baby, "", "", mocktoday) == "Foobar.pdf"
        self.mox.VerifyAll()

class TestPosFactory(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.sposfactory = export.SimplePosFactory(export.Dimensions())
        self.cposfactory = export.ConstraintPosFactory(export.Dimensions())
        self.d1 = datetime.date(2009, 2, 17)
        self.d2 = datetime.date(2008, 8, 1)
        self.d3 = datetime.date(2009, 11, 9)
        self.d4 = datetime.date(2010, 1, 13)

    def test_date_to_coord(self):
        assert self.sposfactory.calc_x_pos(self.d2, 31, self.d2, 1) == 32
        assert self.sposfactory.calc_x_pos(self.d2, 31, self.d1, 1) == 231
        assert self.sposfactory.calc_x_pos(self.d1, 31, self.d3, 1) == 313
        assert self.sposfactory.calc_x_pos(self.d1, 31, self.d4, 1) == 378

    def test_constraints_simple(self):
        baby = models.Baby.objects.get(pk = 2)
        (pos1, pos2) = self.cposfactory.calculate_layout(baby.birth_date, 1, baby.get_sorted_milestones())
        assert pos1.data.id == 18
        assert pos2.data.id == 17
        assert pos1.y == 47
        assert pos2.y == 47
        assert pos2.height == 95

    def test_constraints_overlap(self):
        self.cposfactory.dim = export.Dimensions(max_x = 100, max_y = 200, pic_height = 60.0, factor=3)
        baby = models.Baby.objects.get(pk = 2)
        ms = baby.get_sorted_milestones()
        ms.append(models.Milestone(baby = baby, type = "FREE", note="lalalala", date = datetime.date(2001, 12, 31)))
        (pos1, pos2, pos3) = self.cposfactory.calculate_layout(baby.birth_date, 1, ms)
        assert pos1.data.id == 18
        assert pos3.data.id == 17
        assert pos1.y == 30
        assert pos2.y == 41
        assert int(pos3.y) == 30
        assert pos3.height == 60

    def test_constraints_resize_image(self):
        self.cposfactory.dim = export.Dimensions(max_x = 100, max_y = 200, pic_height = 80.0, factor=3)
        baby = models.Baby.objects.get(pk = 2)
        ms = baby.get_sorted_milestones()
        ms.append(models.Milestone(baby = baby, type = "PHOTO", date = datetime.date(2001, 12, 31), image="6_kuerbis.jpg"))
        (pos1, pos2, pos3) = self.cposfactory.calculate_layout(baby.birth_date, 1, ms)
        assert pos1.height == 64.8
        assert pos1.y == 32
        assert pos2.y == 132

class ExportConfigTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.test1 = export.ExportConfig()
        self.test2 = export.ExportConfig(orientation_landscape = False, months_per_page = 3, pic_size = "SMALL")
        self.mox = mox.Mox()
        self.drawmock = self.mox.CreateMock(export.CairoPDFDrawEngine)

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_simple(self):
        assert self.test1.dim.max_x == 842.0
        assert self.test1.dim.max_y == 598.0
        assert self.test1.dim.factor == 0.49881235154394299
        assert self.test1.dim.pic_height == 95.0

    def test_complex(self):
        assert self.test2.dim.max_y == 842.0
        assert self.test2.dim.max_x == 598.0
        assert self.test2.dim.factor == 0.17558528428093645
        assert self.test2.dim.pic_height == 45.0

    def check_keys(self, keys):
        return lambda x: x.keys().sort() == keys.sort()

    def check_pos(self, posx, posy, width):
        return lambda x: int(x.x) == posx and int(x.y) == posy and int(x.width) == width

    def test_export_mock(self):
        conf = export.ExportConfig(orientation_landscape = False, pic_size = "BIG", months_per_page = 4, gradient = False, font_size = 12, font = "Serif", text_color = (0, 0, 1), grad_color_from = (1, 0, 0))
        mexp = export.Exporter(self.drawmock, export.SimplePosFactory(conf.dim), conf)
        self.drawmock.prepare_export(u'Foobar', '', '')
        self.drawmock.draw_background()
        self.drawmock.draw_axis(mox.Func(self.check_keys(['November', 'December', 'January', 'February', 'March'])))
        self.drawmock.draw_event(mox.Func(self.check_pos(116, 3, 54)))
        self.drawmock.draw_event(mox.Func(self.check_pos(151, 815, 23)))
        self.drawmock.finish_page()
        self.drawmock.draw_background()
        self.drawmock.draw_axis(mox.Func(self.check_keys(['March', 'April', 'May', 'June', 'July'])))
        self.drawmock.finish_page()
        self.drawmock.draw_background()
        self.drawmock.draw_axis(mox.Func(self.check_keys(['July', 'August', 'September', 'October', 'November'])))
        self.drawmock.draw_photo(mox.Func(self.check_pos(207, -110, 112)))
        self.drawmock.finish_page()
        self.drawmock.save_file()
        self.mox.ReplayAll()
        mocktoday = datetime.date(2002, 8, 1)
        mexp.export(models.Baby.objects.get(pk=2), "", "", today=mocktoday)
        self.mox.VerifyAll()

    @attr("only")
    def test_export_real(self):
        conf = export.ExportConfig(orientation_landscape = False, pic_size = "BIG", months_per_page = 4, gradient = False, font_size = 12, font = "Serif", text_color = (0, 0, 1), grad_color_from = (1, 0, 0))
        cpf = export.ConstraintPosFactory(conf.dim)
        cairo = export.CairoPDFDrawEngine(conf)
        exporter = export.Exporter(cairo, cpf, conf)
        mocktoday = datetime.date(2002, 8, 1)
        exporter.export(models.Baby.objects.get(pk=2), "", "", today=mocktoday) # warum bleibt das stecken???

class CairoExportTest(TestCase):

    def setUp(self):
        conf = export.ExportConfig()
        self.cpf = export.ConstraintPosFactory(conf.dim)
        self.cairo = export.CairoPDFDrawEngine(conf)
        self.exporter = export.Exporter(self.cairo, self.cpf, conf)

    def test_svg_export(self):
        self.exporter.export(models.Baby.objects.get(pk=1), "", "")

class FormTest(TestCase):
    fixtures = ['test_data.json']

    def test_baby_form(self):
        b = forms.BabyForm({'name' : 'foobar',
                            'birth_date_0' : '2009-02-11',
                            'birth_date_1' : '18:45:00',
                            'size_in_cm' : '46',
                            'weight_in_g' : '3565',
                            'user' : '6'})
        assert b.is_valid()
        assert b.save().id

    def test_date_time_widget(self):
        d = forms.DateTimeWidget()
        assert d.decompress("") == (datetime.date.today(), None)
        assert d.decompress("2010/12/31 15:32") == ["2010/12/31", "15:32"]
        assert d.decompress(datetime.datetime(2009, 2, 17, 18, 45, 01)) == (datetime.date(2009, 2, 17), "18:45")
        assert d.value_from_datadict({'foo' : 1, 'birth_date_0' : '2009-11-09', 'birth_date_1' : '19:11'}, {}, 'birth_date') == ["2009-11-09", "19:11"]

    def test_milestone_form(self):
        m = forms.MilestoneForm({'baby' : 2, 'date' : '01/01/2000'})
        assert not m.is_valid()
        m = forms.MilestoneForm({'baby' : 1, 'date' : '01/01/2010', 'type' : 'SMILE'})
        assert not m.is_valid()
        m = forms.MilestoneForm({'baby' : 1, 'date' : '01/01/2008', 'type' : 'SLEEP'})
        assert not m.is_valid()
        m = forms.MilestoneForm({'baby' : 1, 'date' : '01/01/2010', 'note' : 'foobar'})
        assert m.is_valid()
        m = forms.MilestoneForm({'baby' : 1, 'date' : '01/01/2010', 'image' : 'kuerbis.jpg'})
        assert m.is_valid()
        assert m.save().id

