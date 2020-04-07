# -*- coding: utf-8 -*-
import logging
from werkzeug.exceptions import Forbidden
from odoo import http, tools, _ 
import pprint
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_event_country_default.controllers.main import WebsiteEventCountryController
from odoo.addons.website_event.controllers.main import WebsiteEventController


_logger = logging.getLogger(__name__)

class WebsiteEventCountryControllerInherit(WebsiteEventCountryController):


    @http.route()
    def address(self, **kw):
        if request.session.session_token:
            return super(WebsiteEventCountryControllerInherit, self).address(**kw)

        first_attendee_email = request.session['1-email']
        address_partner = request.env['res.partner'].sudo().search([("email", '=', first_attendee_email)], limit=1)

        #address_data = super(WebsiteEventCountryControllerInherit, self).address(**kw)
        """override this controller to get the default country of event when and set while rendoring address details"""
        Partner = request.env['res.partner'].with_context(
            show_address=1).sudo()
        order = request.website.sale_get_order()

        if address_partner:
            order.partner_id = address_partner.id

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))
        if address_partner:
            partner_id = address_partner.id


        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search(
                    [('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search(
                        [('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            kw['field_required'] = u'phone,company_name,firstname,surname'
            firstname = kw['firstname'] or ""
            surname = kw['surname'] or ""
            kw['name'] = firstname + " " + surname
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(
                mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(
                order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                partner = request.env['res.partner'].sudo().browse([partner_id])
                if 'firstname' in kw:
                    partner.sudo().write({'firstname': kw['firstname']})
                if 'surname' in kw:
                    partner.sudo().write({'surname': kw['surname']})

                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.partner_id.company_name = partner.company_name
                    if (not partner.parent_id and partner.company_name):
                        existing_company = request.env['res.partner'].search([('name', '=', partner.company_name)])
                        if not existing_company:
                            new_company = request.env['res.partner'].sudo().create({
                                'name': partner.company_name,
                                'company_name': partner.company_name,
                                'is_company': True,
                                'lang': partner.lang,
                                'street': partner.street,
                                'city': partner.city,
                                'zip': partner.zip,
                                'country_id': partner.country_id.id,
                                'company_id': partner.company_id.id,
                                'vat': partner.vat,
                            })
                            partner.parent_id = new_company.id
                        else:
                            partner.parent_id = existing_company.id
                    order.partner_invoice_id = partner.parent_id.id
                    order.onchange_partner_id()
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [
                    (4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/checkout')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'address_partner': address_partner,
            'partner_id': address_partner.id,
            # Get country from order line or sale order
            'event_country_id': order.order_line and order.order_line[0].event_id.address_id.country_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }
        return request.render("website_sale.address", render_values)


class WebsiteEventUseExistingPartner(WebsiteEventController):

    @http.route()
    def registration_confirm(self, event, **post):
        order = request.website.sale_get_order(force_create=1)
        res = super(WebsiteEventUseExistingPartner, self).registration_confirm(event, **post)
        request.session["1-email"] = post['1-email']
        if request.session.session_token:
            if order.partner_id.parent_id:
                order.sudo().write({'partner_invoice_id': order.partner_id.parent_id.id})
        return res


class WebsiteSaleController(WebsiteSale):

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        for f in self._get_mandatory_billing_fields():
            if not f == 'company_name':
                if not order.partner_id[f]:
                    return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        order.sudo().write({'partner_invoice_id': order.partner_id.parent_id.id})

        values = self.checkout_values(**post)

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []

        # Required fields from form
        required_fields = filter(None, (all_form_values.get('field_required') or '').split(','))
        # Required fields from mandatory field function
        required_fields += mode[1] == 'shipping' and ["firstname", "surname", "street", "city", "country_id"] or ["firstname", "surname", "email", "street", "city", "country_id"]
        # Check if state required
        if data.get('country_id'):
            country = request.env['res.country'].browse(int(data.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']

        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        Partner = request.env['res.partner']
        if data.get("vat") and hasattr(Partner, "check_vat"):
            if data.get("country_id"):
                data["vat"] = Partner.fix_eu_vat_number(data.get("country_id"), data.get("vat"))
            check_func = request.website.company_id.vat_check_vies and Partner.vies_vat_check or Partner.simple_vat_check
            vat_country, vat_number = Partner._split_vat(data.get("vat"))
            if not check_func(vat_country, vat_number):
                error["vat"] = 'error'

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message