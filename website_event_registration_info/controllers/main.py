# -*- coding: utf-8 -*-
import json
import logging
from werkzeug.exceptions import Forbidden

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController

_logger = logging.getLogger(__name__)


class WebsiteEventControllerMoreInfo(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/registration/new'],
                type='json', auth="public", methods=['POST'], website=True)
    def registration_new(self, event, **post):
        tickets = self._process_tickets_details(post)
        if not tickets:
            return False

        lang_ids = request.env['res.lang'].search([])

        return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details", {
            'tickets': tickets,
            'event': event,
            'lang_ids': lang_ids,
        })
