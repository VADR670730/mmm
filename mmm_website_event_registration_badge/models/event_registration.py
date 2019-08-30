# -*- coding: utf-8 -*-
"""
Extend event.event to register a custom transparent PNG used as a backgroun image
for printing a Butterfly 1-1 Badge (86mm x 97 mm
"""
import tempfile
import logging
import base64
import os
import urllib

from odoo import models, fields, api, _

from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

from PIL import Image

_logger = logging.getLogger(__name__)


class EventRegistrationPrint(models.Model):
    _inherit = 'event.registration'
    BADGE_WIDTH_PX = 97 * mm
    BADGE_HEIGHT_PX = 86 * mm
    LOGO_WIDTH_PX_MAX = 125
    LOGO_HEIGHT_PX_MAX = 62

    is_badge_printed = fields.Boolean(default=False)
    export_file = fields.Binary(attachment=True, help="This field holds the generated badge.", readonly=True)

    @api.multi
    def print_badge_multi(self):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path) + "/../static/src"

        pdfmetrics.registerFont(TTFont('OpenSans-CondBold', dir_path + "/css/OpenSans-CondBold-webfont.ttf"))
        pdfmetrics.registerFont(TTFont('OpenSans-CondLight', dir_path + "/css/OpenSans-CondLight-webfont.ttf"))

        # Initiate the PDF
        pdf_temp_file = tempfile.NamedTemporaryFile(delete=False)
        c = Canvas(pdf_temp_file.name, pagesize=A4)

        for badge in self:	
            c.translate(mm, mm)

            # Get the badge background image
            (badge_container_x, badge_container_y) = (7 * mm, 7 * mm)
            badge_container_img_path = dir_path + "/img/badge_fa2018.png"
            if badge.event_id.badge_container_img:
                badge_container_data = base64.decodestring(badge.event_id.badge_container_img)
                badge_container_temp_file = tempfile.NamedTemporaryFile(delete=False)
                badge_container_temp_file.write(badge_container_data)
                badge_container_temp_file.close()
                badge_container_img_path = badge_container_temp_file.name

            # Put the badge background on the PDF
            # NOTE: setting mask to 'auto' allow to handle properly PNG with alpha layer
            # LEFT BADGE
            c.drawImage(badge_container_img_path,
                        badge_container_x, badge_container_y,
                        width=self.BADGE_WIDTH_PX, height=self.BADGE_HEIGHT_PX, mask='auto')
            # RIGHT BADGE
            c.drawImage(badge_container_img_path,
                        badge_container_x + self.BADGE_WIDTH_PX, badge_container_y,
                        width=self.BADGE_WIDTH_PX, height=self.BADGE_HEIGHT_PX, mask='auto')

            # Put the attendee name centered on the badge
            if badge.event_id.badge_attendee_name_show:
                text_name = u"{} {}".format(badge.name.title(), badge.last_name.upper())
                font_alias = 'OpenSans-CondBold'
                font_size, do_shorten = self.adaptive_font_string(text_name, font_alias, 28, 28, 15, 94)
                if do_shorten:
                    text_name = badge.get_shortened_name(badge.name, badge.last_name, font_size)
                text_width = stringWidth(text_name, font_alias, font_size)
                text_y = 56 * mm
                text_x = (self.BADGE_WIDTH_PX - text_width) / 2.0
                # Color
                color_code = '000000' #default, black
                if badge.event_id.badge_attendee_name_color_code and ('#' in badge.event_id.badge_attendee_name_color_code):
                    color_code = badge.event_id.badge_attendee_name_color_code.lstrip('#')
                c.setFillColorRGB(
                    float(int(color_code[0:2], 16)) / 256, 
                    float(int(color_code[2:4], 16)) / 256, 
                    float(int(color_code[4:6], 16)) / 256)
                #c.setFillColorRGB(0, 0, 0)
                c.setFont(font_alias, font_size)
                # LEFT BADGE
                c.drawString(badge_container_x + text_x, text_y, text_name)
                # RIGHT BADGE
                c.drawString(badge_container_x + text_x + self.BADGE_WIDTH_PX, text_y, text_name)

            # Put the attendee company name centered on the badge
            if badge.event_id.badge_company_show:
                text_name = badge.company or '      '
                font_alias = 'OpenSans-CondLight'
                font_size, do_shorten = self.adaptive_font_string(text_name, font_alias, 17, 17, 14, 94)
                if do_shorten:
                    text_name = badge.get_shortened_name('', badge.company or '      ', 40)
                text_width = stringWidth(text_name, font_alias, font_size)
                text_y = 48 * mm
                text_x = (badge.BADGE_WIDTH_PX - text_width) / 2.0
                # Color
                color_code = '000000' #default, black
                if badge.event_id.badge_company_color_code and ('#' in badge.event_id.badge_company_color_code):
                    color_code = badge.event_id.badge_company_color_code.lstrip('#')
                c.setFillColorRGB(
                    float(int(color_code[0:2], 16)) / 256, 
                    float(int(color_code[2:4], 16)) / 256, 
                    float(int(color_code[4:6], 16)) / 256)
                c.setFont(font_alias, font_size)
                # LEFT BADGE
                c.drawString(badge_container_x + text_x, text_y, text_name)
                # RIGHT BADGE
                c.drawString(badge_container_x + text_x + self.BADGE_WIDTH_PX, text_y, text_name)

            # Put the url and pin centered on the badge
            if badge.event_id.badge_url_show:
                text_name = badge.get_url_pin_resource(30)
                font_alias = 'OpenSans-CondLight'
                font_size, do_shorten = self.adaptive_font_string(text_name, font_alias, 15, 15, 12, 94)
                if do_shorten:
                    text_name = badge.get_url_pin_resource(30, do_shorten)
                text_width = stringWidth(text_name, font_alias, font_size)
                text_y = 34 * mm
                text_x = (badge.BADGE_WIDTH_PX - text_width) / 2.0
                # Color
                color_code = '000000' #default, black
                if badge.event_id.badge_url_color_code and ('#' in badge.event_id.badge_url_color_code):
                    color_code = badge.event_id.badge_url_color_code.lstrip('#')
                c.setFillColorRGB(
                    float(int(color_code[0:2], 16)) / 256, 
                    float(int(color_code[2:4], 16)) / 256, 
                    float(int(color_code[4:6], 16)) / 256)
                c.setFont(font_alias, font_size)
                # LEFT BADGE
                c.drawString(badge_container_x + text_x, text_y, text_name)
                # RIGHT BADGE
                c.drawString(badge_container_x + text_x + self.BADGE_WIDTH_PX, text_y, text_name)

            # Put the table number in the right position
            if badge.event_id.badge_table_show:
                if badge.table_id and 100 > badge.table_id.table_number > 0:
                    text_name = str(badge.table_id.table_number)
                    font_alias = 'OpenSans-CondBold'
                    font_size = 30
                    text_width = stringWidth(text_name, font_alias, font_size)
                    text_y = 12 * mm
                    text_x = badge_container_x + 16*mm + 2
                    # Color
                    color_code = '000000' #default, black
                    if badge.event_id.badge_table_color_code and ('#' in badge.event_id.badge_table_color_code):
                        color_code = badge.event_id.badge_table_color_code.lstrip('#')
                    c.setFillColorRGB(
                        float(int(color_code[0:2], 16)) / 256, 
                        float(int(color_code[2:4], 16)) / 256, 
                        float(int(color_code[4:6], 16)) / 256)
                    c.setFont(font_alias, font_size)
                    # LEFT BADGE
                    c.drawString(badge_container_x + text_x, text_y, text_name)
                    # RIGHT BADGE
                    c.drawString(badge_container_x + text_x + badge.BADGE_WIDTH_PX, text_y, text_name)

                # Put the table logo picture in the right box
                if badge.table_id and badge.table_id.sponsor_logo is not None:
                    img_logo_data = base64.decodestring(badge.table_id.sponsor_logo)
                    img_logo_temp_file = tempfile.NamedTemporaryFile(delete=False)
                    img_logo_temp_file.write(img_logo_data)
                    img_logo_temp_file.close()
                    img_logo = Image.open(img_logo_temp_file.name).convert("RGBA")
                    w_logo, h_logo = img_logo.size
                    if w_logo > self.LOGO_WIDTH_PX_MAX:
                        h_logo = self.LOGO_WIDTH_PX_MAX * h_logo / w_logo
                        w_logo = self.LOGO_WIDTH_PX_MAX
                    if h_logo > self.LOGO_HEIGHT_PX_MAX:
                        w_logo = self.LOGO_HEIGHT_PX_MAX * w_logo / h_logo
                        h_logo = self.LOGO_HEIGHT_PX_MAX
                    # LEFT BADGE
                    c.drawImage(img_logo_temp_file.name,
                                badge_container_x + 50 * mm, 11 * mm,
                                width=w_logo, height=h_logo, mask='auto')
                    # RIGHT BADGE
                    c.drawImage(img_logo_temp_file.name,
                                badge_container_x + 50 * mm + self.BADGE_WIDTH_PX, 11 * mm,
                                width=w_logo, height=h_logo, mask='auto')
            # Save Page
            c.showPage()
            # Update status:
            badge.is_badge_printed = True

        # Save PDF and stream it
        c.save()
        fn = open(pdf_temp_file.name, 'r')
        self[0].export_file = base64.encodestring(fn.read())
        fn.close()

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?' + urllib.urlencode({
                'model': 'event.registration',
                'field': 'export_file',
                'id': self[0].id,
                'filename': 'a_badge.pdf',
            }),
            'target': 'blank',
        }

    @staticmethod
    def get_shortened_name(first_name, last_name, max_chars):
        """ Return a shortened version of a string based on max allowed value """
        if not last_name:
            last_name = ''
        if not first_name:
            first_name = ''
        if len(last_name) >= max_chars:
            # shorten the last name too
            if len(first_name) == 0:
                return u"{}-".format(last_name[0:max_chars].upper())
            else:
                return u"{}. {}-".format(first_name[0:1].capitalize(), last_name[0:(max_chars-3)].upper())
        elif len(first_name) + len(last_name) >= max_chars:
            if len(first_name) == 0:
                return "{}".format(last_name.upper())
            else:
                return u"{}. {}".format(first_name[0:1].capitalize(), last_name.upper())
        else:
            return u"{} {}".format(first_name.title(), last_name.upper())

    @api.multi
    def get_url_pin_resource(self, max_chars, do_shorten=False):
        """ Return a formatted line for polls """
        if self.poll_url and self.poll_code:
            if do_shorten:
                return u"URL: {}- / PIN: {}".format(self.poll_url[0:max_chars-len(self.poll_code)], self.poll_code)
            else:
                return u"URL: {} / PIN: {}".format(self.poll_url, self.poll_code)
        elif self.poll_url and not self.poll_code:
            if do_shorten:
                return u"URL: {}-".format(self.poll_url[0:max_chars])
            else:
                return u"URL: {}".format(self.poll_url)
        elif not self.poll_url and self.poll_code:
            if do_shorten:
                return u"PIN: {}-".format(self.poll_code[0:max_chars])
            else:
                return u"PIN: {}".format(self.poll_code)
        else:
            return " "

    @staticmethod
    def adaptive_font_string(text, font_alias, font_size_in, max_font_size, min_font_size, max_text_width):
        if font_size_in > max_font_size:
            font_size_in = max_font_size
        text_width = int(stringWidth(text, font_alias, font_size_in) / mm)
        font_size = font_size_in
        do_shorten = False
        if text_width > max_text_width:
            if font_size_in <= min_font_size:
                # stop there: we don't have a font small enough
                do_shorten = True
            else:
                font_size_in -= 1
                font_size, do_shorten = EventRegistrationPrint.adaptive_font_string(text, font_alias, font_size_in, max_font_size, min_font_size, max_text_width)
        return font_size, do_shorten
