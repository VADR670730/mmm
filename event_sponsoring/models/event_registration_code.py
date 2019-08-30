# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import uuid
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EventRegistrationCode(models.Model):
    _inherit = 'mail.thread'
    _name = 'event.registration.code'
    _description = 'Event Registration Code'
    _order = "state desc"

    QUOTA_AVAILABLE = 0
    QUOTA_REACHED = -1
    QUOTA_NONE = -2

    name = fields.Char(required=True)
    code = fields.Char(readonly=True, default=lambda self: _('New'))
    discount_rate = fields.Float(default=0.0, track_visibility='always')
    sponsoring_id = fields.Many2one('event.sponsoring', 'Linked Sponsor', required=True, default=None)
    event_id = fields.Many2one('event.event', 'Linked event', required=True, track_visibility='always')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('cancel', 'Cancelled')], string='Status', default='draft', track_visibility='always')

    total_codes = fields.Integer(string="Vouchers total", track_visibility='always')
    available_quota = fields.Integer(compute='_compute_used_registration_code', 
                                     string='Vouchers available')
    used_codes_count = fields.Integer(compute='_compute_used_registration_code',
                                      readOnly=True, stringer="Vouchers used")
    attendee_ids = fields.One2many('event.registration', 'registration_code',
                                   string='Linked attendees', default=[])

    def get_total_codes_count(self):
        """ because comuted fields somehow don't reach portal """
        return self.total_codes

    @api.depends('attendee_ids')
    def _compute_used_registration_code(self):
        for code in self:
            code.used_codes_count = len(code.attendee_ids)
            code.available_quota = code.total_codes - code.used_codes_count

    def generate_code(self, event_id, sponsoring_id):
        """
        generate a unique registration code formatted as follow:
        XMAS-BMWX-1E64AC8c
        """
        str_event = "".join(self.env['event.event'].browse(event_id).name.split()).ljust(4, 'A').upper()[:4]
        str_sponsor = "".join(self.env['event.sponsoring'].browse(sponsoring_id).name.split()).ljust(4, 'X').upper()[:4]
        str_uuid = str(uuid.uuid4()).upper()[:8]
        return str_event + '-' + str_sponsor + '-' + str_uuid

    @api.one
    def get_code_from_quota(self):
        if self.state == 'confirmed':
            if self.available_quota > 0:
                return self.id
            else:
                return self.QUOTA_REACHED
        else:
            return self.QUOTA_NONE

    @api.model
    def create(self, values):
        """over write method to create Code"""
        if values.get('code', _('New')) == _('New'):
            values['code'] = self.generate_code(values['event_id'], values['sponsoring_id'])
        return super(EventRegistrationCode, self).create(values)

    def write(self, vals):
        return super(EventRegistrationCode, self).write(vals)

    @api.multi
    def button_cancel(self):
        """always be able to cancel"""
        return self.write({'state': 'cancel'})

    @api.multi
    def button_draft(self):
        """always be able to revert to draft"""
        return self.write({'state': 'draft'})

    """def send_pending_invites(self):
        for attendee_id in self.attendee_ids:
            if attendee_id.state == 'open':
                attendee_id.confirm_registration()
        return True
    """

    @api.multi
    def button_confirm(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def unlink(self):
        for code in self:
            if code.state != 'draft':
                raise UserError(_("You can not delete a non draft code."))
            if len(code.attendee_ids) > 0:
                raise UserError(_("You can not delete a code linked to attendees."))
        return super(EventRegistrationCode, self).unlink()
