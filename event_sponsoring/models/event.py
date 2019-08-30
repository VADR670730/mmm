# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
from odoo import api, models, fields, _


class Event(models.Model):
    _inherit = "event.event"

    sponsoring_ids = fields.One2many('event.sponsoring.line', 'event_id', string='Sponsoring')
    registration_code_ids = fields.One2many('event.registration.code', 'event_id', string='Registration codes')
    registration_code_count = fields.Integer('# Codes', compute='_compute_registration_code_count')
    registration_code_mandatory = fields.Boolean('Registration via a code is mandatory', default=False)

    @api.multi
    def _compute_registration_code_count(self):
        for event in self:
            event.registration_code_count = len(event.registration_code_ids)
