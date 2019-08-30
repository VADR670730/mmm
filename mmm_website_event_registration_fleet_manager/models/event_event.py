# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = 'event.event'

    sub_event_ids = fields.One2many('event.sub.event', 'event_id', string="Sub events")
