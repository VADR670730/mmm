# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp


class SaleOrderTemplate(models.Model):
    _name = 'sale.order.template'
    _description = 'Quotation Template'
    _order = 'id desc'

    name = fields.Char(string='Quotation Template Name', required=True)
    order_lines = fields.One2many('sale.order.template.line', 'order_id', string='Order Lines', copy=True)

    @api.model
    def _default_note(self):
        return self.env.user.company_id.sale_note

    note = fields.Text('Terms and conditions', default=_default_note)

    @api.multi
    def action_template_quotation(self):
        sale_view = self.env['ir.models.data'].xmlid_to_res_id('sale.view_order_form', raise_if_not_found=True)

        template_id = False
        for template in self:
            template_id = template

        created_records = []

        for line in template_id.order_lines:
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

        return {
            'name': _('Create Quotation From Template'),
            'view_type': 'form',
            'res_model': 'sale.order',
            'view_id': sale_view,
            'context': {
                'default_template_id': template_id.id,
                'default_note': template_id.note,
                'default_order_line': created_records,
                'default_client_order_ref': template_id.name
            },
            'type': 'ir.actions.act_window',
            'view_mode': 'form'
        }


class SaleOrderTemplateLine(models.Model):
    _name = 'sale.order.template.line'
    _description = 'Quotation Template Line'
    _order = 'order_id desc, id'

    order_id = fields.Many2one('sale.order.template', string='Order Reference', required=True, ondelete='cascade',
                               index=True, copy=False)
    name = fields.Text(string='Description', required=True)

    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True, store=True)

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
                                   default=1.0)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the SOT line.
        """
        for line in self:
            line.update({
                'price_subtotal': line.price_unit * line.product_uom_qty
            })

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        # if not self.product_id:
        #     return {'domain': {'product_uom': []}}

        vals = {}
        # domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        # if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
        #     vals['product_uom'] = self.product_id.uom_id
        #     vals['product_uom_qty'] = 1.0

        product = self.product_id

        name = product.name
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        vals['product_uom_qty'] = 1.0
        vals['price_unit'] = product.price

        self.update(vals)
        # return {'domain': domain}
