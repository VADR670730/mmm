# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteEventSaleConfirm(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order = request.env['sale.order'].sudo().browse([sale_order_id])

        res = super(WebsiteEventSaleConfirm, self).payment_confirmation(**post)

        sale_order.sudo().action_option()
        sale_order.sudo().action_confirm()
        sale_order.sudo().action_invoice_create(final=True)

        return res

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        order = request.website.sale_get_order()
        request.session['sale_last_order_id'] = order.id

        return super(WebsiteEventSaleConfirm, self).payment_validate()
