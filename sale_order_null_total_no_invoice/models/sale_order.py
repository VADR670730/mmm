# -*- coding: utf-8 -*-

from odoo import models, api

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def write(self, vals):
        if self.state == "sale":
            total = 0
            for line in self.order_line:
                total += line.price_subtotal
            if not total:
                vals['invoice_status'] = 'no'
        return super(SaleOrder, self).write(vals)