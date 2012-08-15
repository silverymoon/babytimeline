# This Python file uses the following encoding: utf-8
from django.utils.translation import ugettext as _
from django.conf import settings

import calendar
import constraint
import random
import cairo
import datetime

import models

class Position:

    def __init__(self, x, y, size=(0, 0), data=None):
        self.width = size[0]
        self.height = size[1]
        self.x = x - self.width / 2.0
        self.y = y - self.height
        self.mid_x = x
        self.data = data

    def __repr__(self):
        return "(%d, %d, %dx%d): %s" %(self.x, self.y, self.width, self.height, self.data)

    def __str__(self):
        return "(%d, %d, %dx%d): %s" %(self.x, self.y, self.width, self.height, self.data)

class Dimensions:

    def __init__(self, factor = 0.5, max_x = 842.0, max_y = 598.0, pic_height = 95.0, font_size = 8, text_sizer = lambda x: (len(x) * 2.6, 7)):
        self.min_x = 0
        self.min_y = 0
        self.factor = factor
        self.max_x = max_x
        self.max_y = max_y
        self.mid_y = self.max_y / 2
        self.pic_height = pic_height
        self.font_size = font_size
        self.text_sizer = text_sizer

class ExportConfig:

    def __init__(self, pic_size = "MEDIUM", orientation_landscape = True, months_per_page = 12, gradient = True, grad_color_from = (0, 0, 0), grad_color_to = (1, 1, 1), text_color = (1, 1, 1), font = "Sans", font_size = 8, locale="en"):
        self.pic_size = pic_size
        self.orientation_landscape = orientation_landscape
        self.months_per_page = months_per_page
        self.gradient = gradient
        self.grad_color_from = grad_color_from
        self.grad_color_to = grad_color_to
        self.text_color = text_color
        self.font = font
        self.font_size = font_size
        self.dim = Dimensions(font_size = self.font_size, pic_height = self.pic_height(), max_x = self.max_x(), max_y = self.max_y(), factor = self.factor())
        self.delta = self.delta()
        self.locale = locale

    def pic_height(self):
        if self.pic_size == "BIG":
            return 140.0
        if self.pic_size == "SMALL":
            return 45.0
        return 95.0

    def max_x(self):
        if not self.orientation_landscape:
            return 598.0
        return 842.0

    def max_y(self):
        if not self.orientation_landscape:
            return 842.0
        return 598.0

    def factor(self):
        # Faktor heisst, soviele Pixel pro Tag
        # wenn alles normal, 12 Monate und LANDSCAPE, ist Factor mit  ~ 0.5 gut - 842 Pixel und 365 Tage
        return self.months_per_page * 35.0 / self.max_x()

    def delta(self):
        if self.months_per_page == 12:
            return datetime.timedelta(365)
        return datetime.timedelta(self.months_per_page * 31)

class Exporter:

    def __init__(self, drawengine, posfactory, conf):
        self.conf = conf
        self.drawengine = drawengine
        self.posfactory = posfactory

    def layout(self, baby, date, milestones):
        birth_pos = self.calculate_last_tick(date, self.conf.dim.factor)
        return self.posfactory.calculate_layout(date, birth_pos, milestones)

    def draw_elem(self, pos):
        if pos.data.is_photo():
            self.drawengine.draw_photo(pos)
        else:
            self.drawengine.draw_event(pos)

    def export(self, baby, prefix, suffix, today = datetime.date.today()):
        self.drawengine.prepare_export(baby.name, prefix, suffix)
        date = baby.birth_date.date()
        everything = baby.get_sorted_milestones()
        everything.insert(0, models.Milestone(date=date, type="BIRTH", note=baby.birth_data()))
        while date <= today:
            self.export_year(baby, date, self.filter_milestones_delta(everything, date, self.conf.delta))
            date = date + self.conf.delta
        file = self.drawengine.save_file()
        return file

    def filter_milestones_delta(self, milestones, date, delta):
        return [ ms for ms in milestones if date <= ms.date and date + delta > ms.date ]

    def export_year(self, baby, from_d, milestones):
        self.drawengine.draw_background()
        layout = []
        if len(milestones) > 0:
            layout = self.layout(baby, from_d, milestones)
        self.draw_timeline(from_d, layout)
        self.drawengine.finish_page()

    def draw_timeline(self, date, layout):
        self.drawengine.draw_axis(self.create_ticks(date, self.conf.dim.factor, self.conf.months_per_page + 1))
        for elem in layout:
            self.draw_elem(elem)

    def calculate_month_length(self, year, month, factor):
        return calendar.monthrange(year, month)[1] / factor

    def calculate_last_tick(self, date, factor):
        prev_month = date.month - 1
        prev_year = date.year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        return self.calculate_month_length(prev_year, prev_month, factor)

    def create_ticks(self, date, factor, month_num):
        ticks = {}
        cur_month = date.month
        cur_year = date.year
        last_tick = self.calculate_last_tick(date, factor)
        for i in range(month_num):
            if cur_month > 12:
                cur_year += 1
                cur_month = 1
            ticks[last_tick] = unicode(calendar.month_name[cur_month], 'utf-8')
            last_tick += self.calculate_month_length(cur_year, cur_month, factor)
            cur_month += 1
        return ticks

class CairoPDFDrawEngine():

    def __init__(self, exportconfig):
        self.conf = exportconfig
        self.dim = exportconfig.dim
        self.context = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, self.dim.max_x, self.dim.max_y))
        self.dim.text_sizer = lambda x: self.text_size(x)

    def text_size(self, text):
        self.context.select_font_face(self.conf.font)
        self.context.set_font_size(self.dim.font_size)
        (_x, _y, width, height, _xa, _ya) = self.context.text_extents(text)
        return (width, height)

    def draw_background(self):
        if self.conf.gradient:
            pat = cairo.LinearGradient(self.dim.mid_y, self.dim.min_x, self.dim.mid_y, self.dim.max_x)
            pat.add_color_stop_rgba(0.005, self.conf.grad_color_from[0], self.conf.grad_color_from[1], self.conf.grad_color_from[2], 1)
            pat.add_color_stop_rgba(0.5, self.conf.grad_color_to[0], self.conf.grad_color_to[1], self.conf.grad_color_to[2], 1)
            pat.add_color_stop_rgba(0.995, self.conf.grad_color_from[0], self.conf.grad_color_from[1], self.conf.grad_color_from[2], 1)
        else:
            pat = cairo.SolidPattern(self.conf.grad_color_from[0], self.conf.grad_color_from[1], self.conf.grad_color_from[2])
        self.context.rectangle(self.dim.min_x, self.dim.min_y, self.dim.max_x, self.dim.max_y)
        self.context.set_source(pat)
        self.context.fill()

    def draw_line(self, x1, y1, x2, y2, width, dash=False):
        self.context.set_line_width(width)
        self.context.set_source_rgb(self.conf.text_color[0], self.conf.text_color[1], self.conf.text_color[2])
        self.context.move_to(x1, y1)
        self.context.line_to(x2, y2)
        if dash:
            self.context.set_dash([1, 1])
        self.context.stroke()
        self.context.set_dash([])

    def draw_axis(self, ticks):
        self.draw_line(self.dim.min_x, self.dim.mid_y, self.dim.max_x, self.dim.mid_y, 1)
        for (pos, text) in ticks.items():
            self.draw_line(pos, self.dim.mid_y - 2, pos, self.dim.mid_y + 4, 0.5)
            (width, _h) = self.text_size(text)
            self.draw_text(Position(pos - width / 2.0, self.dim.mid_y + 4), text)

    def draw_photo(self, pos):
        width, height = pos.data.resize_height(pos.height)
        self.draw_line(pos.mid_x, pos.y, pos.mid_x, self.dim.mid_y, 0.5, True)
        self.context.rectangle(pos.x, pos.y, width, height)
        self.context.stroke()
        img = cairo.ImageSurface.create_from_png(pos.data.get_png_file())
        imgpat = cairo.SurfacePattern(img)
        imgpat.set_filter(cairo.FILTER_BEST)
        self.imgcontext.save()
        self.imgcontext.translate(pos.x, pos.y)
        self.imgcontext.scale(width / pos.data.image.width, height / pos.data.image.height)
        self.imgcontext.set_source(imgpat)
        self.imgcontext.paint()
        self.imgcontext.restore()

    def draw_text(self, pos, text):
        self.context.select_font_face(self.conf.font)
        self.context.set_font_size(self.dim.font_size)
        (width, height) = self.text_size(text)
        self.context.move_to(pos.x, pos.y + height)
        self.context.show_text(text)

    def draw_event(self, pos):
        y = pos.y - 1
        if pos.y <= self.dim.mid_y:
            y = pos.y + 5 # needs to be higher below middle
        self.draw_line(pos.mid_x, self.dim.mid_y, pos.mid_x, y, 0.5, True)
        self.draw_text(pos, pos.data.get_text_date(locale = self.conf.locale))

    def prepare_export(self, name, prefix, suffix):
        self.filename = prefix + name + suffix + ".pdf"
        self.surface = cairo.PDFSurface(self.filename, self.dim.max_x, self.dim.max_y)
        self.context = cairo.Context(self.surface)
        self.context.set_antialias(cairo.ANTIALIAS_GRAY)
        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_GRAY)
        self.context.set_font_options(fo)
        self.prepare_images()

    def prepare_images(self):
        self.imgsurface = cairo.PDFSurface("/tmp/foo.pdf", self.dim.max_x, self.dim.max_y)
        self.imgcontext = cairo.Context(self.imgsurface)

    def finish_page(self):
        self.context.set_source_surface(self.imgsurface)
        self.context.paint()
        self.context.show_page()
        self.prepare_images()

    def save_file(self):
        self.surface.flush()
        self.surface.finish()
        return self.filename

class SimplePosFactory:

    def __init__(self, dimensions):
        self.top = True
        self.count = 0
        self.dim = dimensions

    def make_pos(self, x, y, elem, height):
        if elem.is_photo():
            size = elem.resize_height(height)
        else:
            size = self.dim.text_sizer(elem.get_text())
        return Position(x, y, size=size, data=elem)

    def calculate_layout(self, birth, birth_tick, events):
        list = []
        for event in events:
            list.append(self.make_pos(self.calc_x_pos(birth, birth_tick, event.date, 1), self.calc_y_pos(), event, self.dim.pic_height))
        return list

    def calc_x_pos(self, birth, birth_tick, date, factor):
        day_iy = self.day_in_year(date)
        birth_iy = self.day_in_year(birth)
        if date.year > birth.year:
            day_iy += 365 * (date.year - birth.year)
        diff = day_iy - birth_iy
        return birth_tick + (birth.day + diff) / factor

    def day_in_year(self, date):
        return int(date.strftime("%j"))

    def calc_y_pos(self):
        self.count += 1
        pos = self.count * 10
        if pos > self.dim.max_y:
            pos = 10
        if self.top:
            y = pos
            self.top = False
        else:
            y = self.dim.max_y - pos
            self.top = True
        return y

class ConstraintPosFactory(SimplePosFactory):

    def __init__(self, dimensions):
        SimplePosFactory.__init__(self, dimensions)
        self.problem = constraint.Problem(constraint.RecursiveBacktrackingSolver())

    def build_list(self, solution):
        for (key, value) in solution.items():
            key.y = value
        results = solution.keys()
        results.sort(lambda a, b: cmp(a.x, b.x))
        return results

    def calculate_layout(self, birth, birth_tick, events):
        pic_h = self.dim.pic_height
        list = self.calculate_layout_once(birth, birth_tick, events, pic_h)
        while not list:
            pic_h *= 0.9
            print "no solution :(, trying again with %d" %pic_h
            list = self.calculate_layout_once(birth, birth_tick, events, pic_h)
        return list

    def away_from_lines(self, pos, margin):
        return lambda a: a + pos.height < self.dim.max_y - margin and (a + pos.height < self.dim.mid_y - margin or a > self.dim.mid_y + margin)

    def no_overlap(self, pos1, pos2, margin):
        return lambda a, b: (a + pos1.height + margin < b or a > b + pos1.height + margin) and (a + pos2.height + margin < b or a > b + pos2.height + margin)

    def calculate_layout_once(self, birth, birth_tick, events, height):
        self.problem.reset()
        variables = []
        for event in events:
            x_pos = self.calc_x_pos(birth, birth_tick, event.date, self.dim.factor)
            pos = self.make_pos(x_pos, -1, event, height)
            variables.append(pos)
        margin = height / 2.0
        domain = range(int(self.dim.min_y + margin), int(self.dim.mid_y - margin))
        domain += range(int(self.dim.mid_y + margin), int(self.dim.max_y - margin))
        self.problem.addVariables(variables, domain)
        margin = 15
        for var1 in variables:
            self.problem.addConstraint(self.away_from_lines(var1, margin), (var1,))
            for var2 in variables:
                margin = 3
                if var1 != var2 and var1.x < var2.x and var1.x + var1.width + margin >= var2.x:
                    self.problem.addConstraint(self.no_overlap(var1, var2, margin), [var1, var2])
        solu = self.problem.getSolution()
        if solu:
            return self.build_list(solu)
        return []

