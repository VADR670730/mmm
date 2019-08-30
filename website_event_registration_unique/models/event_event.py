# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class EventEventSingke(models.Model):
    _inherit = 'event.event.ticket'

    single_registration = fields.Boolean(string="Single", default=False)