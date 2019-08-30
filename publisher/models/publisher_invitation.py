# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Invitation(models.Model):
    _name = 'publisher.invitation'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)
    active = fields.Boolean(string='Is Active', copy=False, default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)
    partner_count = fields.Integer(string="Partner Count", compute='_compute_partner_count')
    partner_ids = fields.Many2many('res.partner', string="Partners")

    @api.one
    def _compute_partner_count(self):
        self.partner_count = len(self.env['res.partner'].search([('invitation_ids.id', '=', self.id)]))