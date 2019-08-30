# -*- coding: utf-8 -*-
""" Partner gender class"""
from odoo import api, fields, models, _


class ResPartnerGender(models.Model):
    _name = "res.partner.gender"
    _order = 'name'

    name = fields.Char(string="Gender", required=True, translate=True)
    code = fields.Char(string='Code', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', "Gender name already exists !")]

    @api.one
    @api.depends('code')
    def _compute_display_name(self):
        self.display_name = self.code
