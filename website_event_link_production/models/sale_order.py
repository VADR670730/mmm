# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        # if the lines are linked to an event, also link the linked to the production linked to this event
        for order in self:
            for line in order.order_line:
                if line.event_id and line.event_id.production_id:
                    line.production_id = line.event_id.production_id

        return res
