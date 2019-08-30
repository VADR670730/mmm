# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class EventEventTableNumbers(models.Model):
    _inherit = 'event.event'

    event_tables_number = fields.Integer(string="Tables", readonly=True, compute="_compute_tables")

    @api.multi
    def _compute_tables(self):
        self.event_tables_number = self.env['event.event.table'].search_count([('event_id', '=', self.id)])
