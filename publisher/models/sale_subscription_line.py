# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    partner_shipping_id = fields.Many2one('res.partner', string="Shipping Contact")
    language_id = fields.Many2one('res.lang', string="Language")
    free_subscription = fields.Boolean(related='analytic_account_id.free_subscription')

    @api.onchange('product_id', 'quantity')
    def onchange_product_id(self):
        domain = super(SaleSubscriptionLine, self).onchange_product_id()
        contract = self.analytic_account_id
        company_id = contract.company_id.id
        pricelist_id = contract.pricelist_id.id
        context = dict(self.env.context, company_id=company_id, force_company=company_id, pricelist=pricelist_id, quantity=self.quantity)

        if self.product_id:
            partner = contract.partner_id.with_context(context)
            if partner.lang:
                context.update({'lang': partner.lang})

            product = self.product_id.with_context(context)

            self.price_unit = product.lst_price

            if self.uom_id.id != product.uom_id.id:
                self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)

        return domain