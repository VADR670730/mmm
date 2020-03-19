# -*- coding: utf-8 -*-
import logging
from werkzeug.exceptions import Forbidden
from odoo import http
import pprint
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_event_country_default.controllers.main import WebsiteEventCountryController
from odoo.addons.website_event.controllers.main import WebsiteEventController


_logger = logging.getLogger(__name__)

class WebsiteEventCountryControllerInherit(WebsiteEventCountryController):

    @http.route()
    def address(self, **kw):
        first_attendee_email = request.session['1-email']
        address_partner = request.env['res.partner'].sudo().search([("email", '=', first_attendee_email)], limit=1)

        address_data = super(WebsiteEventCountryControllerInherit, self).address(**kw)
        """override this controller to get the default country of event when and set while rendoring address details"""
        Partner = request.env['res.partner'].with_context(
            show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

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

                if mode[1] == 'billing':
                    order.partner_id = partner_id
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
            'partner_id': partner_id,
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

        res = super(WebsiteEventUseExistingPartner, self).registration_confirm(event, **post)

        request.session["1-email"] = post['1-email']

        return res


class WebsiteSaleController(WebsiteSale):

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        sale_order = request.website.sale_get_order()

        res = super(WebsiteSaleController, self).checkout(**post)

        if sale_order and sale_order.partner_id.name != "Public user" and sale_order.partner_id.email:
            sale_order_partner = sale_order.partner_id
            sale_order_partner_shipping = sale_order.partner_shipping_id
            #sale_order_partner_invoice = sale_order.partner_invoice_id
            existing_partner = request.env["res.partner"].sudo().search([('id', '!=', sale_order_partner.id),('email', '=ilike', sale_order.partner_id.email),
            ('type','!=','delivery'), ('type','!=','invoice')], limit=1)
            if existing_partner:
                sale_order.sudo().write({'partner_id': existing_partner.id})
                # if sale_order_partner == sale_order_partner_invoice:
                #     sale_order.sudo().write({'partner_invoice_id': existing_partner.id})
                if existing_partner.parent_id:
                    sale_order.sudo().write({'partner_invoice_id': existing_partner.parent_id.id, 'partner_shipping_id': existing_partner.id})
                else: 
                    sale_order.sudo().write({'partner_invoice_id': existing_partner.id, 'partner_shipping_id': existing_partner.id})
                #sale_order.sudo().write({'partner_shipping_id': existing_partner.id})
                sale_order_partner_shipping.sudo().unlink()
                sale_order_partner.sudo().unlink()
            else:
                company_id = None
                existing_company = request.env['res.partner'].sudo().search([('name', '=ilike', sale_order_partner.company_name), ('is_company','=', True)])
                if existing_company:
                    company_id = existing_company
                else:
                    company_id = request.env['res.partner'].sudo().create({
                        'name': sale_order_partner.company_name,
                        'is_company': True,
                        'lang': sale_order_partner.lang,
                        'street': sale_order_partner.street,
                        'city': sale_order_partner.city,
                        'zip': sale_order_partner.zip,
                        'country_id': sale_order_partner.country_id.id,
                        'vat': sale_order_partner.vat,
                    })
                new_partner = request.env['res.partner'].sudo().create({
                    'name': sale_order_partner.name,
                    'phone': sale_order_partner.phone,
                    'email': sale_order_partner.email,
                    'lang': sale_order_partner.lang,
                    'parent_id': company_id.id,
                    'type': 'other',
                    'street': sale_order_partner.street,
                    'city': sale_order_partner.city,
                    'zip': sale_order_partner.zip,
                    'country_id': sale_order_partner.country_id.id,
                    'child_ids': sale_order_partner.child_ids
                })
                sale_order.sudo().write({'partner_id': new_partner.id, 'partner_invoice_id': new_partner.parent_id.id, 'partner_shipping_id': new_partner.id})
                sale_order_partner_shipping.sudo().unlink()
                sale_order_partner.sudo().unlink()

        return res