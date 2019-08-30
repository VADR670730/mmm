# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    event_role_ids = fields.Many2many('event.role', 'event_role_event_rel',
                                      'event_id', 'rol_id',
                                      string='Event Roles')
    is_role_selection_mandatory = fields.Boolean(
        'Role Selection Mandatory', translate=True)
