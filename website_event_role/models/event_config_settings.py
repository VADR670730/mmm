# -*- coding: utf-8 -*-

from odoo import fields, models


class EventConfigSettings(models.TransientModel):
    _inherit = 'event.config.settings'

    group_event_role_management = fields.Selection([
        (0, 'No Event Roles'),
        (1, 'Manage Event Roles')
    ], "Event Role Management",
        default=1,
        translate=True,
        implied_group='website_event_role.group_event_role_management',
        help="""Manage Roles in Event""")
