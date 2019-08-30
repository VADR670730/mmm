# -*- coding: utf-8 -*-

import logging
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController

_logger = logging.getLogger(__name__)


class WebsiteEventRoleController(WebsiteEventController):

    def _process_tickets_details(self, data):
        """Override this method website_event from in order to pass sub events and event roles
            in ticket"""
        ticket_post = {}
        for key, value in data.items():
            if not key.startswith('nb_register') or '-' not in key:
                continue
            items = key.split('-')
            if len(items) < 2:
                continue
            ticket_post[int(items[1])] = int(value)
        tickets = request.env['event.event.ticket'].browse(tuple(ticket_post))
        ticket = tickets
        if len(tickets) > 1:
            ticket = tickets[0]
        data = super(WebsiteEventRoleController, self)._process_tickets_details(data)
        is_role_management = request.env['res.users'].sudo().has_group('website_event_role.group_event_role_management')
        for detail in data:
            detail.update({
                'is_mandatory': ticket.event_id.is_role_selection_mandatory,
                'is_role_management': is_role_management,
                'event_roles': [sub_event_role_id for sub_event_role_id in ticket.event_id.event_role_ids],
            })
        return data
