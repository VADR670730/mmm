# -*- coding: utf-8 -*-

import logging
from odoo.http import request
from odoo import http, tools, _
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.website_event_sale_multicompany.controllers.main import WebsiteEventControllerMultiCompany

_logger = logging.getLogger(__name__)


class WebsiteSubEventsController(WebsiteEventController):

    def _process_tickets_details(self, data):
        """Override this method from website_event_role in order to pass sub_event_line and ticket_price
            in ticket"""
        process_data = super(WebsiteSubEventsController, self)._process_tickets_details(data)
        for detail in process_data:
            ticket_id = detail.get('id')
            if ticket_id:
                is_role_management = request.env['res.users'].sudo().has_group('website_event_role.group_event_role_management')
                ticket = request.env['event.event.ticket'].sudo().browse(ticket_id)
                hide_sub_event = True
                for sub_event in ticket.event_id.sub_event_line_ids:
                    if len(sub_event.event_role_ids) <= 0:
                        hide_sub_event = False
                        break
                detail.update({
                    'is_role_management': is_role_management,
                    'price': ticket.price,
                    'event_roles': [sub_event_role_id for sub_event_role_id in ticket.event_id.event_role_ids],
                    'hide_sub_event': hide_sub_event,
                    'is_mandatory': ticket.event_id.is_role_selection_mandatory,
                    'sub_event_line_ids': [sub_event_line_id for sub_event_line_id in ticket.event_id.sub_event_line_ids]})
        _logger.debug("\n\n Data : %s", process_data)
        return process_data

    def _process_registration_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = super(WebsiteSubEventsController, self)._process_registration_details(details)
        counter = 1
        for registration in registrations:
            if 'sub_event_line_ids' in registration:
                registration['sub_event_line_ids'] = request.httprequest.form.getlist(str(counter) + '-sub_event_line_ids')
                counter += 1
        return registrations


class WebsiteEventControllerSaleTotalPrice(WebsiteEventControllerMultiCompany):

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
            order.sudo().write(
                {'company_id': first_ticket.event_id.company_id.id})
        total_price_display = False
        for registration in registrations:
            ticket = request.env['event.event.ticket'].sudo().browse(
                int(registration['ticket_id']))
            if float(registration.get('total_price_discounted') or 0.0) > 0.0:
                total_price_display = True

            # Sub event description
            sub_events_description = ""
            if 'sub_event_line_ids' in registration:
                for sub in registration.get('sub_event_line_ids'):
                    sub_event_id = request.env['event.sub.event.line'].sudo().browse(int(sub))
                    sub_events_description += "\n" + sub_event_id.product_id.name
                
            cart_values = order.with_context(
                total_price=registration.get('total_price'),
                event_ticket_id=ticket.id,
                fixed_price=True,
                sub_events_description=sub_events_description,
            )._cart_update(
                product_id=ticket.product_id.id, add_qty=1, registration_data=[registration])
            attendee_ids |= set(cart_values.get('attendee_ids', []))

        # free tickets -> order with amount = 0: auto-confirm, no checkout
        if not total_price_display:
            order.action_confirm()  # tde notsure: email sending ?
            attendees = request.env['event.registration'].browse(
                list(attendee_ids))
            # clean context and session, then redirect to the confirmation page
            request.website.sale_reset()
            return request.render("website_event.registration_complete", {
                'attendees': attendees.sudo(),
                'event': event,
            })

        return request.redirect("/shop/checkout")
