# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteEventControllerInherit(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        order = request.website.sale_get_order(force_create=1)
        res = super(WebsiteEventControllerInherit, self).registration_confirm(event, **post)

        if order:
            order_line = order.order_line
            attendees = request.env['event.registration'].sudo().search([('sale_order_line_id', '=', order_line.id)])
            for attendee in attendees:
                so_line = attendee.sale_order_line_id
                new_so_line_name = "["+attendee.event_id.name+"]\n"+so_line.product_id.name+"\n"+attendee.last_name+" "+attendee.name+" ("+attendee.email+")\n"+attendee.company
                values = {
                    'product_uom': 1,
                    'product_uom_qty': 1,
                    'currency_id': so_line.currency_id.id,
                    'event_ok': so_line.event_ok,
                    'company_id': so_line.company_id.id,
                    'discount_base': so_line.discount_base,
                    'discount': so_line.discount,
                    'commission': so_line.commission,
                    'name': new_so_line_name,
                    'display_name': attendee.display_name,
                    'product_tmpl_id': so_line.product_tmpl_id.id,
                    'event_ticket_id': so_line.event_ticket_id.id,
                    'order_name': so_line.order_name,
                    'order_id': so_line.order_id.id,
                    'invoice_status': so_line.invoice_status,
                    'product_id': so_line.product_id.id,
                    'production_id': so_line.production_id.id,
                    'commission': so_line.commission,
                    'tax_id': so_line.tax_id
                }
                if so_line.price_unit:
                    values['price_unit'] = so_line.price_unit
                if so_line.full_equipment_received:
                    values['full_equipment_received'] = so_line.full_equipment_received
                if so_line.invoice_lines:
                    values['invoice_lines'] = so_line.invoice_lines
                
                so_line_copy = request.env['sale.order.line'].sudo().create(values)
                attendee.sudo().write({'sale_order_line_id': so_line_copy.id})
            if order_line.state == 'sale' or order_line.state == "done":
                order_line.sudo().write({'state': 'draft'})
            order_line.sudo().unlink()

        return res
