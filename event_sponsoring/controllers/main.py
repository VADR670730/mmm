# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.website_event.controllers.main import WebsiteEventController
import csv

_logger = logging.getLogger(__name__)


class WebsiteAccountRegistrationCode(website_account):
    MANDATORY_REGISTRATION_CODE_FIELDS = ['name', 'event_id', 'discount_rate', 'available_quota']

    @http.route(['/my/vouchers/request'],
                type='http', auth="user", website=True)
    def portal_my_vouchers_request(self, **kw):
        """ Prepare data to server the registration code request form
            If everything went well we will redirect to listing page
        """
        Sponsoring = request.env['event.sponsoring']
        partner = request.env.user.partner_id
        domain = [
            ('partner_id.id', '=', partner.parent_id.id),
            ('state', '=', 'open'),
        ]
        my_sponsoring = Sponsoring.sudo().search(domain)
        event_count = 0
        for spon in my_sponsoring:
            for evt in spon.sponsoring_line_ids:
                if evt.state == 'confirm':
                    event_count += 1

        return request.render("event_sponsoring.vouchers_request_followup", {
            'error': {},
            'error_message': [],
            'event_count': event_count,
            'sponsoring': my_sponsoring,
        })

    def registration_code_request_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.MANDATORY_REGISTRATION_CODE_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'
        # event_id validation
        # discount_rate validation
        if data.get('discount_rate'):
            try:
                fdr = float(data.get('discount_rate'))
                if fdr > 100:
                    error['discount_rate'] = 'error'
                    error_message.append(_('Discount rate should not exceed 100.'))
            except ValueError:
                error['discount_rate'] = 'error'
                error_message.append(_('Discount Rate should be a number.'))
        # quota validation

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data.iterkeys() if k not in self.MANDATORY_REGISTRATION_CODE_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message

    @http.route(['/my/vouchers/request/handle'],
                type='http', auth="user", methods=['POST'], website=True)
    def portal_my_vouchers_request_handle(self, redirect=None, **post):
        partner = request.env.user.partner_id
        values = {
            'error': {},
            'error_message': []
        }

        if post:
            error, error_message = self.registration_code_request_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_REGISTRATION_CODE_FIELDS}
                sponsoring_id, event_id = values['event_id'].split('_')
                values.update({
                    'sponsoring_id': int(sponsoring_id),
                    'event_id': int(event_id),
                    'state': 'draft',
                })
                vouchers = request.env['event.registration.code'].create(values)

                # Get Event
                event_id = request.env['event.event'].sudo().search([('id', '=', event_id)], limit=1)

                # Get Sponsor
                sponsoring_id = request.env['event.sponsoring'].sudo().search([('id', '=', sponsoring_id)], limit=1)
                if event_id.user_id.email:
                    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    url = "%s/web#id=%s&view_type=form&model=event.registration.code" % (base_url, vouchers.id)
                    content = _("""Hello %s, <br />A new registration code has been requested<br />for: %s<br />for event: %s<br /><br />See <a href="%s">here</a> to validate it""") % (event_id.user_id.name, sponsoring_id.name, event_id.name, url)
                    mail_id = request.env['mail.mail'].create({
                        'body_html': content,
                        'subject': 'Odoo: Registration Code Request Notification',
                        'email_to': event_id.user_id.email,
                        'email_from': partner.email,
                        'state': 'outgoing',
                        'type': 'email',
                        'auto_delete': True,
                    })
                    request.env['mail.mail'].send([mail_id])
                if redirect:
                    return request.redirect(redirect)
                return request.redirect("/my/vouchers")

        values.update({
            'partner': partner,
            'redirect': redirect,
        })

        return request.render("event_sponsoring.vouchers_request_followup", values)

    @http.route(['/my/vouchers/<int:voucher>/download_csv'],
                type='http', auth="public", website=True)
    def generate_csv(self, voucher=None, **kw):
        event_registration_code = request.env['event.registration.code'].sudo().browse([voucher])
        if event_registration_code:
            fileContent = None
            with open('/tmp/tmp.csv', 'w+') as csvfile:
                filewriter = csv.writer(csvfile, delimiter = ";", quotechar='|', quoting=csv.QUOTE_MINIMAL)
                event_registration_code = request.env['event.registration.code'].sudo().browse([voucher])
                filewriter.writerow([_('Attendee'), _('Company'), _('Email'), _('Table'), _('State')])
                for attendee in event_registration_code.attendee_ids:
                    filewriter.writerow([(attendee.last_name + ' ' + attendee.name).encode('utf-8'), 
                    (attendee.company).encode("utf-8"), 
                    (attendee.email).encode('utf-8'),
                    (str(attendee.table_id.name) + " - " + str(attendee.table_id.table_number)).encode('utf-8'),
                    (attendee.state).encode('utf-8')] )
            
            with open('/tmp/tmp.csv', 'r') as csvfile:
                fileContent = csvfile.read()
                
            return request.make_response(fileContent, [('Content-Type', 'application/octet-stream'),
                                ('Content-Disposition', 'attachment; filename=%s.csv'% _('attendees'))])

    @http.route()
    def account(self, **kw):
        """ Override this in order to add voucher counter badge
            NOTE: we add the draft state to this domain filter so we can also list
            user registration codes requests
        """
        response = super(WebsiteAccountRegistrationCode, self).account(**kw)
        partner = request.env.user.partner_id

        Vouchers = request.env['event.registration.code']
        voucher_count = Vouchers.search_count([
            ('sponsoring_id.partner_id.id', '=', partner.parent_id.id),
            ('state', 'in', ['draft', 'confirmed', 'full', 'cancel']),
            ('event_id.website_published', '=', True)
        ], )
        response.qcontext.update({
            'voucher_count': voucher_count,
        })
        return response

    #
    # Sponsored events registration codes
    #

    @http.route(['/my/vouchers', '/my/vouchers/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_vouchers(self, page=1, date_begin=None, date_end=None, **kw):
        """ New endpoint for managing vouchers listing
        NOTE: we add the draft state to this domain filter so we can also list
        user registration codes requests
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Vouchers = request.env['event.registration.code']

        domain = [
            ('sponsoring_id.partner_id.id', '=', partner.parent_id.id),
            ('state', 'in', ['draft', 'confirmed', 'full', 'cancel']),
            ('event_id.website_published', '=', True)
        ]
        archive_groups = self._get_archive_groups('event.registration.code', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        voucher_count = Vouchers.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/vouchers",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=voucher_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        vouchers = Vouchers.search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'vouchers': vouchers,
            'page_name': 'voucher',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/vouchers',
        })
        return request.render("event_sponsoring.portal_my_vouchers", values)

    @http.route(['/my/vouchers/<int:voucher>'], type='http', auth="user", website=True)
    def vouchers_followup(self, voucher=None, **kw):
        voucher = request.env['event.registration.code'].browse([voucher])
        try:
            voucher.check_access_rights('read')
            voucher.check_access_rule('read')
        except AccessError:
            return request.render("website.403")

        voucher_sudo = voucher.sudo()

        return request.render("event_sponsoring.vouchers_followup", {
            'event': voucher_sudo.event_id.with_context(pricelist=request.website.id),
            'event_ticket_ids ': voucher_sudo.event_id.event_ticket_ids,
            'voucher': voucher_sudo,
        })

    @http.route(['/my/vouchers/<int:voucher>/cancel'], type='http', auth="user", website=True)
    def vouchers_cancel(self, voucher=None, **kw):
        voucher = request.env['event.registration.code'].browse([voucher])

        try:
            voucher.check_access_rights('write')
            voucher.check_access_rule('write')
        except AccessError:
            return request.render("website.403")

        voucher.write({
            'state': 'cancel',
        })
        return request.render("event_sponsoring.vouchers_followup", {
            'voucher': voucher,
        })


class WebsiteEventRegistrationCodesController(WebsiteEventController):

    @http.route(['/event/registration_code/validate_json'],
                type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def registration_code_validate(self, event_id, registration_code, *kw):
        """ Ajax call to validate a voucher  and pass discount"""
        if registration_code:
            reg_code = request.env['event.registration.code'].sudo().search([
                ('code', '=', registration_code),
                ('event_id', '=', int(event_id)),
                ('state', '=', 'confirmed')
            ], limit=1)
            if not reg_code or len(reg_code) != 1:
                return {
                    'registration_code_id': -1,
                    'message': _("--> Invalid Code"),
                }
            elif reg_code.available_quota < 1:
                return {
                    'registration_code_id': -1,
                    'message': _("--> Expired code"),
                }
            else:
                return {
                    'registration_code_id': reg_code.get_code_from_quota(),
                    'registration_code_name': reg_code.name,
                    'registration_discount_rate': reg_code.discount_rate,
                    'registration_code_sponsor_name': reg_code.sponsoring_id.name,
                    'message':  _("--> Code OK, you are invited by: ") + reg_code.sponsoring_id.name + _("(") + reg_code.name + _(")"),
                }

    def _process_registration_details(self, details):
        """Process data posted from the attendee details form."""
        registrations = super(WebsiteEventRegistrationCodesController, self)._process_registration_details(details)
        for registration in registrations:
            if 'registration_code' in registration:
                reg_code = request.env['event.registration.code'].sudo().search([
                    ('code', '=', registration['registration_code'])], limit=1)
                if reg_code:
                    registration['registration_code'] = reg_code[0].id
                else:
                    registration.pop('registration_code')
        return registrations

    def _process_tickets_details(self, data):
        """ Override this one from mmm_website_event_registration_fleet_manager in onrder to pass registration code
            in ticket """
        registration_code = None
        for key, value in data.items():
            if not key.startswith('registration_code') or '-' not in key:
                continue
            items = key.split('-')
            if len(items) == 2:
                registration_code = value
        data = super(WebsiteEventRegistrationCodesController, self)._process_tickets_details(data)
        if registration_code:
            for idx, ticket in enumerate(data):
                data[idx]['registration_code'] = registration_code
        _logger.debug("DATA: %s", data)
        return data
