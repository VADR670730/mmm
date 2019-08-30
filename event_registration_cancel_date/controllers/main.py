# -*- coding: utf-8 -*-
import logging

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_event_registration_info.controllers.main import WebsiteEventControllerMoreInfo

_logger = logging.getLogger(__name__)


class WebsiteEventControllerCivility(WebsiteEventControllerMoreInfo):

    @http.route(['/event/<model("event.event"):event>/registration/new'],
                type='json', auth="public", methods=['POST'], website=True)
    def registration_new(self, event, **post):
        """ Override this in order to add titles """
        tickets = self._process_tickets_details(post)
        if not tickets:
            return False

        lang_ids = request.env['res.lang'].search([])

        titles = request.env['res.partner.title'].sudo().search([])

        return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details", {
            'tickets': tickets,
            'event': event,
            'titles': titles,
            'lang_ids': lang_ids,
        })
