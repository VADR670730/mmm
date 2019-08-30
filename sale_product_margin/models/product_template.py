# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    margin = fields.Float(string="Margin", default=1)
    auto_sale_price = fields.Boolean(string="Auto sale price", default=False)

    @api.onchange('list_price', 'margin', 'auto_sale_price', 'standard_price')
    def _compute_sale_price(self):
        self.ensure_one()

        if self.auto_sale_price:
            self.list_price = self.margin * self.standard_price
            
        