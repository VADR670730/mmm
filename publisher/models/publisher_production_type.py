# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProductionType(models.Model):
    _name = 'publisher.production.type'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)
    active = fields.Boolean(string='Is Active', copy=False, default=True)
    product_category_id = fields.Many2one('product.category', string='Product Category', required=True)
    media_id = fields.Many2one('publisher.media', string='Media', required=True)
    invoicing_mode = fields.Selection([
        ('before', 'Before Publication'),
        ('after', 'After Publication'),
        ('both', 'Before & After Publication')
        ], string='Invoicing Mode', default='before', required=True)
    down_payment = fields.Float(string='Down Payment', default=0, required=True)
    sequence_id = fields.Many2one('ir.sequence', string="Sequence", required=True)
    production_count = fields.Integer(string="Production Count", compute='_compute_production_count')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('publisher.production.type'))
    project_template_id = fields.Many2one('project.project', domain="[('is_template', '=', True')]", string="Project Template", help="When creating a new production for this type, this project will be copied to a new one (including tasks and stages).")
    
    @api.one
    def _compute_production_count(self):
        self.production_count = len(self.env['publisher.production'].search([('production_type_id.id', '=', self.id)]))
