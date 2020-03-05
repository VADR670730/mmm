# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebSiteEventSaleController(WebsiteEventSaleController):

    @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        # This is a copy of the registration_confirm method in webSiteEventSaleController with some modificatition
        # It creates order lines per attendee and delete the previous order line created
        order = request.website.sale_get_order(force_create=1)
        attendee_ids = set()

        registrations = self._process_registration_details(post)
        for registration in registrations:
            ticket = request.env['event.event.ticket'].sudo().browse(int(registration['ticket_id']))
            cart_values = order.with_context(event_ticket_id=ticket.id, fixed_price=True)._cart_update(product_id=ticket.product_id.id, add_qty=1, registration_data=[registration])
            attendee_ids |= set(cart_values.get('attendee_ids', []))
            # From here we get the so_line for the attendees, duplicate it (with different name) and remove it
            so_line = None
            for attendee_id in attendee_ids:
                attendee = request.env['event.registration'].sudo().browse([attendee_id])
                so_line = attendee.sale_order_line_id
                so_line_copy = request.env['sale.order.line'].sudo().create({
                    'product_uom': 1,
                    'product_uom_qty': 1,
                    'currency_id': so_line.currency_id.id,
                    'event_ok': so_line.event_ok,
                    'company_id': so_line.company_id.id,
                    'discount_base': so_line.discount_base,
                    'name': attendee.name,
                    'display_name': attendee.display_name,
                    'product_tmpl_id': so_line.product_tmpl_id.id,
                    'event_ticket_id': so_line.event_ticket_id.id,
                    'order_name': so_line.order_name,
                    'order_id': so_line.order_id.id,
                    'invoice_status': so_line.invoice_status,
                    'product_id': so_line.product_id.id,
                    'production_id': so_line.production_id.id,
                    'discount_base': so_line.discount_base,
                    'commission': so_line.commission,
                    'tax_id': so_line.tax_id.id,
                    'price_unit': so_line.price_unit,
                    'full_equipment_received': so_line.full_equipment_received,
                    'invoice_lines': so_line.invoice_lines
                })
                attendee.sudo().write({'sale_order_line_id': so_line_copy.id})
            if so_line:
                so_line.sudo().unlink()
                
        # free tickets -> order with amount = 0: auto-confirm, no checkout
        if not order.amount_total:
            order.action_confirm()  # tde notsure: email sending ?
            attendees = request.env['event.registration'].browse(list(attendee_ids)).sudo()
            # clean context and session, then redirect to the confirmation page
            request.website.sale_reset()
            return request.render("website_event.registration_complete", {
                'attendees': attendees,
                'event': event,
            })

        return request.redirect("/shop/checkout") 