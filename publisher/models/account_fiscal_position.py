# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    invoice_display = fields.Char(string='To display on invoices')