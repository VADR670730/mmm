# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    event_role_id = fields.Many2one(
        'event.role', string='Event Roles', translate=True, copy=False)
    is_role_selection_mandatory = fields.Boolean(
        related='event_id.is_role_selection_mandatory', copy=False)

    @api.model
    def _prepare_attendee_values(self, registration):
        att_data = super(EventRegistration,
                         self)._prepare_attendee_values(registration)
        event_role_id = registration.get('event_role_id')
        if event_role_id:
            att_data.update({
                'event_role_id': event_role_id
            })
        return att_data
