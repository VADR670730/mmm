# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class EventSponsoring(models.Model):
    """ Event sponsoring. This model defines event sponsoring."""
    _name = 'event.sponsoring'
    _description = 'Event Sponsoring'
    _order = 'name'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Associated Partner',
                                 domain=[('is_sponsor', '=', True)])
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed')], string='Status', default='open')
    sponsoring_line_ids = fields.One2many('event.sponsoring.line', 'sponsoring_id',
                                          string='Linked events', copy=True, auto_join=True)
    registration_codes_ids = fields.One2many('event.registration.code', 'sponsoring_id', string="Codes")

    @api.multi
    def unlink(self):
        for sponsor in self:
            if len(sponsor.sponsoring_line_ids) > 0 or len(sponsor.registration_codes_ids) > 0:
                raise UserError(_("You can not delete a sponsor linked to events or codes."))
        return super(EventSponsoring, self).unlink()


class EventSponsoringLine(models.Model):
    """ This one is a wrapper for events linked to this sponsoring """
    _name = 'event.sponsoring.line'
    _description = 'Event Sponsoring Line'
    _order = 'sponsoring_id, sequence, id'

    sponsoring_id = fields.Many2one('event.sponsoring', 'Associated Sponsoring')
    name = fields.Char(related='event_id.name', readonly=True)
    sequence = fields.Integer(default=10)

    event_id = fields.Many2one('event.event', 'Sponsored event',
                               change_default=True, ondelete='restrict', required=True)
    state = fields.Selection(related='event_id.state', readonly=True, string='Status')

    registration_codes_ids = fields.One2many(related='event_id.registration_code_ids')
