# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    reports_logo = fields.Binary(string="Reports Logo")
    sfc_header = fields.Html(string="Standard Form Contract Header")
    sfc = fields.Html(string="Standard Form Contract")
    bank_acc = fields.Many2one('res.partner.bank', string="Bank Account")
