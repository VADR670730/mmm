# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class EventRegistrationTable(models.Model):
    _inherit = 'event.registration'
    table_id = fields.Many2one('event.event.table', string="Table", domain="[('event_id', '=', event_id)]")
