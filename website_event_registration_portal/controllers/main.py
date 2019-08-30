# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account
import random

_logger = logging.getLogger(__name__)


class WebsiteAccountRegistrationUpdate(website_account):

    @http.route(['/my/account/<string:token>/view'],
                type='http', auth="public", methods=['GET'], website=True)
    def account_view_via_token(self, token=None, **kw):
        _logger.debug("\n\n TOKEN : %s", token)
        if token is None:
            # 401 'Unauthenticated'
            return request.render('website.401')

        Registration = request.env['event.registration']
        record = Registration.sudo().search([('portal_update_token', '=', token)])
        if not record or len(record) != 1:
            # 401 'Unauthenticated'
            return request.render('website.404')

        record = record[0] or record
        attendee = Registration.browse([record.id])

        # Get titles
        titles = request.env['res.partner.title'].sudo().search([])

        return request.render("website_event_registration_portal.attendee_update_form", {
            'attendee': attendee.sudo(),
            'token': token,
            'titles': titles,
        })

    @http.route(['/my/account/<string:token>/update'],
                type='http', auth="public",  methods=['POST'], website=True)
    def account_update_via_token(self, token=None, **post):
        if token is None:
            # 401 'Unauthenticated'
            return request.render('website.401')

        registration = request.env['event.registration']
        record = registration.sudo().search([('portal_update_token', '=', token)])
        if not record or len(record) != 1:
            # 401 'Unauthenticated'
            return request.render('website.404')

        record = record[0] or record
        attendee = registration.browse([record.id])
        values = {}
        values.update(post)
        attendee.sudo().write(values)

        # Get titles
        titles = request.env['res.partner.title'].sudo().search([])

        return request.render("website_event_registration_portal.attendee_update_form", {
            'attendee': attendee.sudo(),
            'token': token,
            'titles': titles,
        })

    @http.route(['/my/account/<string:token>/cancel'],
                type='http', auth="public", methods=['GET'], website=True)
    def account_cancel_via_token(self, token=None, **kw):
        if token is None:
            # 401 'Unauthenticated'
            return request.render('website.401')

        registration = request.env['event.registration']
        record = registration.sudo().search([('portal_update_token', '=', token)])
        if not record or len(record) != 1:
            # 401 'Unauthenticated'
            return request.render('website.404')

        record = record[0] or record
        attendee = registration.browse(record.id)
        attendee.sudo().write({
            'state': 'cancel',
        })

        # Get titles
        titles = request.env['res.partner.title'].sudo().search([])

        return request.render("website_event_registration_portal.attendee_update_form", {
            'attendee': attendee.sudo(),
            'token': token,
            'titles': titles,
        })

    @http.route(['/my/account/<string:token>/anonymize'],
                type='http', auth="public", methods=['GET'], website=True)
    def account_delete_via_token(self, token=None, **kw):
        if token is None:
            # 401 'Unauthenticated'
            return request.render('website.401')

        registration = request.env['event.registration']
        record = registration.sudo().search([('portal_update_token', '=', token)])
        if not record or len(record) != 1:
            # 401 'Unauthenticated'
            return request.render('website.404')

        record = record[0] or record
        attendee = registration.browse(record.id)
        attendee_sudo = attendee.sudo()

        # Anonymize data
        attendee_sudo.write({
            'name': str(random.choice(attendee_sudo.name)) + str(random.randint(0,999)),
            'last_name': str(random.choice(attendee_sudo.last_name)) + str(random.randint(0,999)),
            'company': str(random.choice(attendee_sudo.company)) + str(random.randint(0,999)),
            'company': str(random.choice(attendee_sudo.company)) + str(random.randint(0,999)),
            'function': str(random.choice(attendee_sudo.function)) + str(random.randint(0,999)),
            'email': '',
            'phone': '',
            'is_anonymized': True,
        })
        
        # Get titles
        titles = request.env['res.partner.title'].sudo().search([])

        return request.render("website_event_registration_portal.attendee_update_form", {
            'attendee': attendee_sudo,
            'token': token,
            'titles': titles,
        })
