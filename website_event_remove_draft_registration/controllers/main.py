# -*- coding: utf-8 -*-
import logging
from werkzeug.exceptions import Forbidden
from odoo import http
import pprint
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteSaleController(WebsiteSale):

    # @http.route(['/shop/payment'], type='http', auth="public", website=True)
    # def payment(self, **post):
    #     super(WebsiteSaleController, self).payment()
    #     return request.redirect('/shop/confirmation')

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        sale_order_id = request.session.get('sale_order_id')
        sale_order = request.env['sale.order'].sudo().browse([sale_order_id])
        sale_order.write({'confirmed_by_user': True})
        return super(WebsiteSaleController, self).confirm_order()

    # @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    # def payment_confirmation(self, **post):
    #     super(WebsiteSaleController, self).payment_confirmation()
    #     return request.redirect("/shop/confirm_order")