# -*- coding: utf-8 -*-
import logging
from werkzeug.exceptions import Forbidden
from odoo import http
import pprint
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

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