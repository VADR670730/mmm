# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Event(models.Model):
    _inherit = 'event.event'

    production_id = fields.Many2one('publisher.production' ,string=_("Production"))

    @api.onchange("production_id")
    def onchange_production_id(self):
        for event_registration in self._origin.registration_ids:
            sale_order_line_ids = self.env['sale.order.line'].search([("order_id", '=', event_registration.sale_order_id.id)])
            for sale_order_line in sale_order_line_ids:
                sale_order_line.write({"production_id": self._origin.production_id.id})
