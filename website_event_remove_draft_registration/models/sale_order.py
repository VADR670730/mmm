# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirmed_by_user = fields.Boolean(default=False)

    @api.multi
    def remove_draft_sale_orders(self, args):
        records = self.env['sale.order'].search([('state', '=', "draft"), ('confirmed_by_user', '=', False)])
        for record in records:
            if ( record.state == "draft" and (datetime.utcnow() - datetime.strptime(record.date_order, '%Y-%m-%d %H:%M:%S')) > timedelta(1) ):
                record.unlink()