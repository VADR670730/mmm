# -*- coding: utf-8 -*-
import json
import logging
from werkzeug.exceptions import Forbidden

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController

_logger = logging.getLogger(__name__)


class WebsiteEventControllerMoreInfo(WebsiteEventController):

    def _process_registration_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.iteritems():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                # Added this condition to get the list of selected items in the sub_events list
                if 'sub_event_ids' in field_name:
                    registrations.setdefault(counter, dict())[field_name] = request.httprequest.form.getlist(counter + '-sub_event_ids')
                else:
                    registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.iteritems():
            for registration in registrations.values():
                registration[key] = value
        return registrations.values()

    def _process_tickets_details(self, data):
        ticket_post = {}
        for key, value in data.items():
            if not key.startswith('nb_register') or '-' not in key:
                continue
            items = key.split('-')
            if len(items) < 2:
                continue
            ticket_post[int(items[1])] = int(value)
        tickets = request.env['event.event.ticket'].browse(tuple(ticket_post))
        data = []
        for ticket in tickets:
            if ticket_post[ticket.id]:
                data.append({
                    'id': ticket.id,
                    'name': ticket.name,
                    'quantity': ticket_post[ticket.id],
                    'price': ticket.price,
                    'ask_for_is_fleet_manager': ticket.ask_for_is_fleet_manager,
                    'ask_for_is_participating_blue_run': ticket.ask_for_is_participating_blue_run,
                    'sub_events': [{'id': sub_event.id, 'name': sub_event.name} for sub_event in ticket.event_id.sub_event_ids if len(ticket.event_id.sub_event_ids) > 0],
                })
        return data
