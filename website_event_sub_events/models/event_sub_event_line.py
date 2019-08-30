# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventSubEventLine(models.Model):
    """Added Event Sub Event Line model."""

    _name = 'event.sub.event.line'
    _rec_name = 'product_id'

    name = fields.Char(string="Name", compute='_compute_name')
    event_id = fields.Many2one(
        'event.event', string="Event", translate=True)
    product_id = fields.Many2one(
        'product.product', string="Product", translate=True)
    sale_price = fields.Monetary(string="Price", translate=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    sequence = fields.Integer(string="Sequence", translate=True)
    event_role_ids = fields.Many2many(
        'event.role', string="Roles", translate=True)
    is_role_selection_mandatory = fields.Boolean(
        string="Is Mandatory", related="event_id.is_role_selection_mandatory")

    @api.multi
    def _compute_name(self):
        for sub in self:
            sub.name = '%s (%s %s)' % (sub.product_id.name, sub.sale_price, sub.currency_id.symbol)

    @api.onchange('product_id')
    def onchange_product(self):
        """Sale price field will be changed when product will be selected."""
        self.sale_price = self.product_id.list_price

    @api.multi
    def name_get(self):
        res = []
        for sub in self:
            name = '%s (%s %s)' % (sub.product_id.name, sub.sale_price, sub.currency_id.symbol)
            res.append((sub.id, name))
        return res
