# -*- coding: utf-8 -*-
"""
Guest tables module
"""

import logging
from odoo import models,fields, api, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class EventTable(models.Model):
    """ Main class """
    _name = 'event.event.table'
    _description = "Event Attendee Table"

    _sql_constraints = [
        ('uniq_table_number', 'UNIQUE(event_id.id, table_number)', _("This table number is already attributed")),
        ('uniq_table_name', 'UNIQUE(event_id.id, name)', _("This table name is already in use")),
        ('check_max_att', 'CHECK(attendee_number_max >= attendee_number)', _("More attendees than seats")),
        ('check_max_empty', 'CHECK(attendee_number_max > 0)', _("Table should have at least one seat")),
    ]

    name = fields.Char(required=True)
    sponsor_logo = fields.Binary()
    # might be redundant with name
    table_number = fields.Integer(required=True)
    attendee_ids = fields.One2many('event.registration', 'table_id', string="Attendees")
    # number of attendee per table
    attendee_number = fields.Integer(compute="_get_number_attendees", readonly=True, store=True, default=False)
    attendee_number_max = fields.Integer(string="Max Attendees", required=True, default=0)
    event_id = fields.Many2one('event.event', string='Event')

    @api.one
    @api.depends('attendee_ids')
    def _get_number_attendees(self):
        """ Deduce attendees number """
        self.attendee_number = len(self.attendee_ids)

    @api.onchange('attendee_ids')
    def _max_attendees_warning(self):
        """ Warn while adding attendees """
        if len(self.attendee_ids) > self.attendee_number_max > 0:
            raise UserError(_('Attendees on this table exceed the max set.'))

    @api.onchange('attendee_number_max')
    def _max_number_changer_warning(self):
        """ Warn while setting/changing the number of max person per table"""
        if self.attendee_number_max < self.attendee_number:
            raise UserError(_('Attendees on this table exceed the max set. Remove attendees first'))
