# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class EventEvent(models.Model):
    _inherit = 'event.event'

    disclaimer_registration = fields.Text(translate=True)
