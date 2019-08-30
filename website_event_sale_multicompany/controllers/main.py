# -*- coding: utf-8 -*-
import json
import logging
from werkzeug.exceptions import Forbidden

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteEventControllerMultiCompany(WebsiteEventSaleController):

    @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        order = request.website.sale_get_order(force_create=1)
        registrations = self._process_registration_details(post)
        attendee_ids = set()

        # Here we want to get the company of the event that was selected in order to 
        # create the SO on the correct company
        # Attention, doing this assumes that for Public users, SO, registrations, events, ... are visibles in multi-company-mode
        # The goal is to allow selling a event ticket for a company as the website is linked to another one
        # we will : get the event chosen, then get the company on the event and then change the SO company based on the one found on the event
        first_registration = registrations[0]
        first_ticket = request.env['event.event.ticket'].sudo().browse(int(first_registration['ticket_id']))
        if order.company_id != first_ticket.event_id.company_id:
            order.sudo().write({'company_id': first_ticket.event_id.company_id.id})
        
        for registration in registrations:
            ticket = request.env['event.event.ticket'].sudo().browse(int(registration['ticket_id']))
            cart_values = order.with_context(event_ticket_id=ticket.id, fixed_price=True)._cart_update(product_id=ticket.product_id.id, add_qty=1, registration_data=[registration])
            attendee_ids |= set(cart_values.get('attendee_ids', []))

        # free tickets -> order with amount = 0: auto-confirm, no checkout
        if not order.amount_total:
            order.action_confirm()  # tde notsure: email sending ?
            attendees = request.env['event.registration'].browse(list(attendee_ids))
            # clean context and session, then redirect to the confirmation page
            request.website.sale_reset()
            return request.render("website_event.registration_complete", {
                'attendees': attendees.sudo(),
                'event': event,
            })

        return request.redirect("/shop/checkout")

class WebsiteSaleEventMultiCompant(WebsiteSale):
    
    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        # Do the same for the linked partner, if the order has already been assigned to the correct company, use this one
        partner_id = Partner.sudo().search([('id', '=', partner_id)])
        if partner_id.company_id != request.website.sale_get_order().company_id:
            partner_id.sudo().write({
                'company_id': request.website.sale_get_order().company_id.id})

        return partner_id.id