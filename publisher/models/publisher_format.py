# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Format(models.Model):
    _name = 'publisher.format'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)
    active = fields.Boolean(string='Is Active', copy=False, default=True)
    media_ids = fields.Many2many('publisher.media', string='Medias', required=True)

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('publisher.format'))