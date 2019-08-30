# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class EventRegistrationFleetManager(models.Model):
    _inherit = 'event.registration'

    is_fleet_manager = fields.Boolean()
    is_participating_blue_run = fields.Boolean()
    sub_event_ids = fields.Many2many('event.sub.event', string="Sub events")

    @api.model
    def _prepare_attendee_values(self, registration):
        att_data = super(EventRegistrationFleetManager, self)._prepare_attendee_values(registration)
        if 'sub_event_ids' in att_data:
            att_data['sub_event_ids'] = [(6, 0, [int(sub_event_id) for sub_event_id in att_data['sub_event_ids']])]
        return att_data 
