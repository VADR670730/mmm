# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', _('Draft')),
        ('sent', _('Draft Sent')),
        ('option', _('Option')),
        ('sale', _('Signed')),
        ('done', _('Locked')),
        ('cancel', _('Cancelled')),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.one
    def action_option(self):
        self.state = 'option'

    @api.multi
    def action_draft(self):
        for so in self:
            if so.state == 'option':
                so.state = 'cancel'

        return super(SaleOrder, self).action_draft()

    @api.multi
    def write(self, values):

        if not self.env['res.users'].has_group('sales_team.group_sale_manager'): # user not a manager
            if self.state not in ['draft', 'sent', 'option']: # sale is not a draft or option quotation
                if not values.get('state') or values['state'] not in ['sent', 'draft']: # values['state'] = 'sent' only when printing or sending an email, values['state'] = 'draft' when setting it back to draft
                    raise exceptions.ValidationError(_('You are not allowed to edit the form, please ask a manager'))
                    return False
        
        return super(SaleOrder, self).write(values)