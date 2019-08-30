# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import random

from odoo import api, models, fields, tools, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    total_price = fields.Float('Total Price')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        values = super(SaleOrder, self)._cart_update(
            product_id, line_id, add_qty, set_qty, **kwargs)
        sale_line = self.env['sale.order.line'].browse([values.get('line_id')])
        #Check quantity as if we remove from card then it will not update total price as sale line is not found.
        if values.get('quantity') > 0:
            if self.env.context.get('total_price'):
                sale_line.write({
                    'total_price': self.env.context.get('total_price'),
                    'name': sale_line.name + self.env.context.get('sub_events_description'),
                })
            else:
                sale_line.write({
                    'price_unit': sale_line.total_price,
                })
        return values
