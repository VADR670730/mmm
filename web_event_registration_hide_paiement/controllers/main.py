# -*- coding: utf-8 -*-
import logging
from werkzeug.exceptions import Forbidden
from odoo import http
import pprint
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteSaleController(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        super(WebsiteSaleController, self).payment()
        return request.redirect('/shop/confirmation')