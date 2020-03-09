# -*- coding: utf-8 -*-
import logging
from werkzeug.exceptions import Forbidden
from odoo import http
import pprint
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteSaleController(WebsiteSale):

    # Maybe put it in /shop/payment
    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        sale_order_id = request.session.get('sale_order_id')
        sale_order = request.env['sale.order'].sudo().browse([sale_order_id])
        _logger.debug("\n\n")
        _logger.debug(sale_order.read())

        if sale_order:
            sale_order_partner = sale_order.partner_id
            existing_partner = request.env["res.partner"].sudo().search([('id', '!=', sale_order_partner.id),('email', '=ilike', sale_order.partner_id.email)], limit=1)
            existing_shipping_partner = request.env['res.partner'].sudo().search([('email', '=ilike', sale_order.partner_shipping_id.email), 
            ('type', '=','delivery'), ('street', '=ilike', sale_order.partner_shipping_id.street), ('city', '=ilike', sale_order.partner_shipping_id.city),
            ('zip', '=ilike', sale_order.partner_shipping_id.zip), ('country_id', '=', sale_order.partner_shipping_id.country_id.id), 
            ('state_id', '=', sale_order.partner_shipping_id.state_id.id), ('id', '!=', sale_order.partner_shipping_id.id)], limit=1)
            if existing_partner:
                _logger.debug("\n\nPARTNER ALREADY EXIST")
                sale_order.sudo().write({'partner_id': existing_partner.id})
                if sale_order.partner_invoice_id.id == sale_order_partner.id:
                    sale_order.sudo().write({'partner_invoice_id': existing_partner.id})
                if existing_shipping_partner:
                    if existing_shipping_partner.parent_id.id == existing_partner.id:
                        sale_order.sudo().write({'partner_shipping_id': existing_shipping_partner.id})
                    else:
                        existing_partner.sudo().write({'child_ids': [(existing_shipping_partner.id, existing_partner.child_ids)]})
                        sale_order.sudo().write({'partner_shipping_id': existing_shipping_partner.id})
                    sale_order.partner_shipping_id.sudo().unlink()
                if sale_order.partner_invoice_id.id == sale_order_partner.id:
                    sale_order.sudo().write({'partner_invoice_id': existing_partner.id})
                sale_order_partner.sudo().unlink()
            else:
                company_id = None
                existing_company = request.env['res.partner'].sudo().search([('name', '=ilike', sale_order_partner.company_name), ('company_type','=','company')])
                if existing_company:
                    company_id = existing_company.id
                else:
                    company_id = request.env['res.partner'].sudo().create({
                        'name': sale_order_partner.company_name,
                        'company_type': 'company',
                        'street': sale_order_partner.street,
                        'city': sale_order_partner.city,
                        'zip': sale_order_partner.zip,
                        'country_id': sale_order_partner.country.id,
                        'lang': sale_order_partner.lang
                    })
                new_partner = request.env['res.partner'].sudo().create({
                    'name': sale_order_partner.name,
                    'phone': sale_order_partner.phone,
                    'email': sale_order_partner.email,
                    'lang': sale_order_partner.lang,
                    'parent_id': company_id,
                    'child_ids': sale_order_partner.child_ids
                })
                sale_order.sudo().write({'partner_id': new_partner.id, 'partner_invoice_id': new_partner.id})
                sale_order_partner.sudo().unlink()
        return super(WebsiteSaleController, self).confirm_order()