# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventEvent(models.Model):
    """Inherited Event Event model."""

    _inherit = 'event.event'

    sub_event_line_ids = fields.One2many(
        'event.sub.event.line', 'event_id', string="Roles", translate=True)
    sub_event_count = fields.Integer(
        compute="_event_count", string="Sub Events", translate=True)
    event = fields.Integer()

    @api.one
    @api.depends('sub_event_line_ids')
    def _event_count(self):
        """It will count the sub event of particular event."""
        event = self.env['event.sub.event.line'].search(
            [('event_id', '=', self.id)])
        self.sub_event_count = len(event)
