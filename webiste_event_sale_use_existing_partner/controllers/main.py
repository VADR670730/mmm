# -*- coding: utf-8 -*-
import logging
from werkzeug.exceptions import Forbidden
from odoo import http
import pprint
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteSaleController(WebsiteSale):

    @http.route(['/shop/payment/validate'], type='http', auth="public", website=True)
    def payment_validate(self, **post):
        # This method is a copy of payment_validate method but modified.
        # This method delete the shipping adress and the partner that was created
        # But before, it will create a new contact if no existing was found and create a company if the given one does not exist, if it exists it will be linked to the existing company
        # The sale order partner,shipping_partner and invoice_partner will be the same partner
        sale_order_id = request.session.get('sale_order_id')
        sale_order = request.env['sale.order'].sudo().browse([sale_order_id])

        if sale_order:
            sale_order_partner = sale_order.partner_id
            sale_order_partner_shipping = sale_order.partner_shipping_id
            sale_order_partner_invoice = sale_order.partner_invoice_id
            existing_partner = request.env["res.partner"].sudo().search([('id', '!=', sale_order_partner.id),('email', '=ilike', sale_order.partner_id.email),
            ('type','!=','delivery'), ('type','!=','invoice')], limit=1)
            if existing_partner:
                sale_order.sudo().write({'partner_id': existing_partner.id})
                if sale_order_partner == sale_order_partner_invoice:
                    sale_order.sudo().write({'partner_invoice_id': existing_partner.id})
                sale_order.sudo().write({'partner_shipping_id': existing_partner.id})
                sale_order_partner_shipping.sudo().unlink()
                sale_order_partner.sudo().unlink()
            else:
                company_id = None
                existing_company = request.env['res.partner'].sudo().search([('name', '=ilike', sale_order_partner.company_name), ('is_company','=', True)])
                if existing_company:
                    company_id = existing_company.id
                else:
                    company_id = request.env['res.partner'].sudo().create({
                        'name': sale_order_partner.company_name,
                        'is_company': True,
                        'lang': sale_order_partner.lang
                    })
                new_partner = request.env['res.partner'].sudo().create({
                    'name': sale_order_partner.name,
                    'phone': sale_order_partner.phone,
                    'email': sale_order_partner.email,
                    'lang': sale_order_partner.lang,
                    'parent_id': company_id,
                    'type': 'other',
                    'street': sale_order_partner.street,
                    'city': sale_order_partner.city,
                    'zip': sale_order_partner.zip,
                    'country_id': sale_order_partner.country_id.id,
                    'child_ids': sale_order_partner.child_ids
                })
                sale_order.sudo().write({'partner_id': new_partner.id, 'partner_invoice_id': new_partner.id, 'partner_shipping_id': new_partner.id})
                sale_order_partner_shipping.sudo().unlink()
                sale_order_partner.sudo().unlink()
        return super(WebsiteSaleController, self).payment_validate()