# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ResPartnerSocial(models.Model):
    _inherit = 'res.partner'

    facebook_link = fields.Char(string="Facebook")
    twitter_link = fields.Char(string="Twitter")
    instagram_link = fields.Char(string="Instagram")
    snapchat_link = fields.Char(string="Snapchat")
    linkedin_link = fields.Char(string="Linkedin")