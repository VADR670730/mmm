# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class CertifiedSupplier(models.Model):
    _inherit = 'res.partner'

    supplier_certified = fields.Boolean(string="Certified Supplier", default=False)