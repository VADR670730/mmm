# -*- coding: utf-8 -*-
""" Extend product category to add company field """

import logging
from odoo import models, fields, api, exceptions, _
_logger = logging.getLogger(__name__)


class ProductCategoryCompany(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('product.category'))
