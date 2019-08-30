# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    """Inherited Event Registration model."""

    _inherit = 'event.registration'

    @api.onchange('event_id')
    def change_event(self):
        """If event changes its Price,Sub Event and Ticket will disappear."""
        for each_reg in self:
            each_reg.total_price = 0
            each_reg.sub_event_line_ids = False
            each_reg.event_ticket_id = False
            each_reg.event_role_id = False

    @api.depends('event_ticket_id', 'sub_event_line_ids')
    def change_price(self):
        """Price is calculated when event and sub event will be selected."""
        if self.registration_code:
            for each_reg in self:
                total = 0
                percent = 0
                if each_reg.event_ticket_id:
                    total += each_reg.event_ticket_id.price
                for sub_events in each_reg.sub_event_line_ids:
                    total += sub_events.sale_price
                percent = 100 - self.registration_code.discount_rate
                each_reg.total_price = total * percent / 100
        else:
            for each in self:
                total = 0
                if each.event_ticket_id:
                    total += each.event_ticket_id.price
                for sub_events in each.sub_event_line_ids:
                    total += sub_events.sale_price
                each.total_price = total

    total_price = fields.Float(
        string="Total Price", compute='change_price', translate=True)
    sub_event_line_ids = fields.Many2many(
        'event.sub.event.line', string="Sub Events", translate=True)

    @api.model
    def _prepare_attendee_values(self, registration):
        att_data = super(EventRegistration,
                         self)._prepare_attendee_values(registration)
        if 'sub_event_line_ids' in att_data:
            att_data['sub_event_line_ids'] = [
                (6, 0, [int(sub_event_id) for sub_event_id in att_data['sub_event_line_ids']])]
        return att_data
