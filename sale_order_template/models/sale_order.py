# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    template_id = fields.Many2one('sale.order.template', string="Template")

    @api.onchange('template_id')
    def _onchange_template_id(self):

        created_records = []

        if self.template_id:
            for line in self.template_id.order_lines:
                created_records.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_id.uom_id.id,

                    'invoice_status': 'no',
                    'procurement_ids': [],
                    'qty_invoiced': 0,
                    'qty_delivered_updateable': False
                }))

            self.note = self.template_id.note
            self.order_line = created_records
            self.client_order_ref = self.template_id.name

    @api.multi
    def action_quotation_template(self):
        template_view = self.env['ir.models.data'].xmlid_to_res_id('sale_order_template.view_sale_order_template_form',
                                                                   raise_if_not_found=True)

        so_id = False
        for so in self:
            so_id = so

            created_records = []

            for line in so_id.order_line:
                created_records.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'product_uom_qty': line.product_uom_qty,
                    'price_subtotal': line.price_unit * line.product_uom_qty
                }))

            return {
                'name': _('Create Template From Sale Order'),
                'view_type': 'form',
                'res_model': 'sale.order.template',
                'view_id': template_view,
                'context': {
                    'default_name': _('From') + ' ' + so_id.name + ((' (' + so_id.client_order_ref + ')') if (so_id.client_order_ref and so_id.client_order_ref != '') else ''),
                    'default_note': so_id.note,
                    'default_order_lines': created_records
                },
                'type': 'ir.actions.act_window',
                'view_mode': 'form'
            }
