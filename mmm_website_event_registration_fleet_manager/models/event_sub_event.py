# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class EventSubEvent(models.Model):
    _name = 'event.sub.event'

    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    event_id = fields.Many2one('event.event', string="Event", required=True)
    registration_ids = fields.Many2many('event.registration', string="Registrations")
    registration_count = fields.Integer(compute='_compute_registration_count')
    sequence = fields.Integer()

    @api.one
    def _compute_registration_count(self):
        self.registration_count = len(self.registration_ids)
    
