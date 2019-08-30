# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import uuid
import logging
from odoo import models, fields, api, exceptions, _
from datetime import datetime

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _inherit = 'event.event'

    maximum_portal_edit_date = fields.Datetime(string="Maximum portal edit date", help="Fill this date if you wanto to forbit attendees to edit their data on the portal beyond this date.")

    @api.multi
    def is_registration_editable(self):
        self.ensure_one()
        if not self.maximum_portal_edit_date:
            return True
        return datetime.now() <  datetime.strptime(self.maximum_portal_edit_date, '%Y-%m-%d %H:%M:%S')
