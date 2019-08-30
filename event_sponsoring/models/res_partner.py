# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
from odoo import api, models, fields, _


class ResPartner(models.Model):

    _inherit = ['res.partner']

    is_sponsor = fields.Boolean('Is A Sponsor', default=False)
