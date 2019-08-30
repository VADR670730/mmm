# -*- coding: utf-8 -*-
""" Extend partner title to include all gender(s) associated to this title"""
from odoo import api, fields, models, _


class PartnerTitle(models.Model):
    _inherit = "res.partner.title"

    gender_ids = fields.Many2many('res.partner.gender')
