# -*- coding: utf-8 -*-
"""
Extend event.event to register a custom transparent PNG used as a backgroun image
for printing a Butterfly 1-1 Badge (86mm x 97 mm
"""
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class EventEventBadgeContainer(models.Model):
    _inherit = 'event.event'

    badge_container_img = fields.Binary()

    badge_attendee_name_show = fields.Boolean(string="Show attendee name", default=True)
    badge_attendee_name_color_code = fields.Char(string="Color for attendee name", help="Insert an hexadecimal code as #ABCDEF", default="#000000", required=True)

    badge_company_show = fields.Boolean(string="Show company name", default=True)
    badge_company_color_code = fields.Char(string="Color for company", help="Insert an hexadecimal code as #ABCDEF", default="#000000", required=True)

    badge_url_show = fields.Boolean(string="Show url", default=True)
    badge_url_color_code = fields.Char(string="Color for url", help="Insert an hexadecimal code as #ABCDEF", default="#000000", required=True)

    badge_table_show = fields.Boolean(string="Show table", default=True)
    badge_table_color_code = fields.Char(string="Color for table", help="Insert an hexadecimal code as #ABCDEF", default="#000000", required=True)

    @api.multi
    def get_badge_skin_resource(self):
        """ Registration badge printing: return a custom skin if any defined. Otherwise return default one """
        img_url = "background: transparent url('{}')"
        if self.badge_container_img:
            return img_url.format("data:image/jpg;base64," + self.badge_container_img)
        else:
            return img_url.format("/mmm_website_event_registration_badge/static/src/img/badge_fa2018.png")
