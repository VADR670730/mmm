# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions

from odoo import models, fields, api, exceptions, _

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    cancel_date = fields.Datetime(string="Cancel Date")

    @api.multi
    def write(self, vals):
        if 'state' in vals:
            if vals['state'] == 'cancel':
                vals.update({'cancel_date': datetime.today()})
        return super(EventRegistration, self).write(vals)
