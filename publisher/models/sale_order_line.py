# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
import datetime

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    production_id = fields.Many2one('publisher.production', string="Production")
    format_id = fields.Many2one('publisher.format', string="Format")
    location_id = fields.Many2one('publisher.location', string="Location")
    date_start = fields.Date(string='Publication Date')
    date_end = fields.Date(string='End Date')
    full_equipment_received = fields.Boolean(string='Full Equipment Received')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    attachment_count = fields.Integer(string="Attachment Count", compute='_compute_attachment_count')
    sequence_computed = fields.Integer(string="Sequence Order", compute='_compute_sequence_computed')

    format_needed = fields.Boolean(related='production_id.production_type_id.media_id.format_needed', string="Format Needed")
    location_needed = fields.Boolean(related='production_id.production_type_id.media_id.location_needed', string="Location Needed")
    date_start_needed = fields.Boolean(related='production_id.production_type_id.media_id.date_start_needed', string="Publication Date Needed")
    date_end_needed = fields.Boolean(related='production_id.production_type_id.media_id.date_end_needed', string="End Date Needed")

    media_id = fields.Many2one(related='production_id.production_type_id.media_id', string="Media")
    product_category_id = fields.Many2one('product.category', string="Product Category", compute='_compute_product_category_id')

    discount_base = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    commission = fields.Float(string='Agency Commission (%)', digits=dp.get_precision('Discount'), default=lambda self: self._get_default_comission())

    prod_state = fields.Selection(related='production_id.state', string="Production State")

    qty_to_invoice_confirmed = fields.Float(
        compute='_get_to_invoice_qty_confirmed', string='To Invoice', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    qty_invoiced_confirmed = fields.Float(
        compute='_get_invoiced_qty_confirmed', string='Invoiced', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))

    order_name = fields.Char(related='order_id.name', string='Order')

    @api.model
    def _get_default_comission(self):
        if self._context.get('link_agency') and self._context.get('final_customer_id') and self._context.get('agency_id'):
            customer_parent_id = self.env['res.partner'].search([('id', '=', self._context.get('final_customer_id'))])
            partner_relation_id = self.env['res.partner.link'].search([
                '|',
                    '&',
                        ('right_partner_id', '=', int(self._context.get('final_customer_id'))),
                        ('left_partner_id', '=', int(self._context.get('agency_id'))),
                    '&',
                        ('right_partner_id', '=', customer_parent_id.parent_id.id),
                        ('left_partner_id', '=', int(self._context.get('agency_id')))
            ])
            return partner_relation_id.agency_comission
        return 0.0


    @api.onchange('discount_base', 'commission')
    def _compute_discount(self):
        for line in self:
            line.discount = (1.0 - (100.0-self.discount_base)/100.0 * (100.0-self.commission)/100.0) * 100.0

    def _check_publisher_fields(self, vals):

        production_id = self.env['publisher.production'].search([('id', '=', vals['production_id'])]) if vals.get('production_id') else self.production_id

        if not production_id:
            return True

        location_id = self.env['publisher.location'].search([('id', '=', vals['location_id'])]) if vals.get('location_id') else self.location_id
        name = vals.get('name') or self.name

        if location_id:
            if location_id.unique:
                for line in production_id.sale_line_ids:
                    if line.id != self.id:
                        if location_id.id == line.location_id.id:
                            raise exceptions.ValidationError(_('Line ') + name + _(' : Another line (') + line.order_id.name + ' - ' + line.name + _(') in the production (') + production_id.name + _(') has the same location which is set as unique.'))
                            return False
            if location_id.unique_time_range:
                self_date_start = vals.get('date_start', self.date_start)
                self_date_end = vals.get('date_end', self.date_end)

                if self_date_start and self_date_end:
                    for line in production_id.sale_line_ids:
                        if line.id != self.id:
                            if location_id.id == line.location_id.id:
                                if self_date_start <= line.date_end and self_date_end >= line.date_start:
                                    raise exceptions.ValidationError(_('Line ') + name + _(' : Another line (') + line.order_id.name + ' - ' + line.name + _(') in the production (') + production_id.name + _(') has the same location which is set as unique for a time range but overlaps.'))
                                    return False

        return True

    @api.model
    def create(self, vals):
        if not self._check_publisher_fields(vals):
            return False

        return super(SaleOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if not self._check_publisher_fields(vals):
            return False

        if self.production_id:
            if 'full_equipment_received' in vals:
                self.production_id.message_post(subject=self.name, body=self.name + " : " + (_("Full equipment is received") if vals['full_equipment_received'] else _("Equipment set as not received")))
            if 'attachment_ids' in vals and vals['attachment_ids'][0][0] == 6:
                delta = len(vals['attachment_ids'][0][2]) - len(self.attachment_ids)
                self.production_id.message_post(subject=self.name, body=self.name + " : " + str(abs(delta)) + " " + (_(" attachment(s) added") if delta>0 else _(" attachment(s) deleted")))
        return super(SaleOrderLine, self).write(vals)

    @api.onchange('production_id')
    def _onchange_production_id(self):
        if self.production_id and self.product_id and self.product_id not in self.env['product.product'].search([('categ_id', 'child_of', self.production_id.production_type_id.product_category_id.id)]):
            self.product_id = False

    @api.onchange('product_id')
    def _onchange_product_id(self):

        media_id = self.production_id.production_type_id.media_id if self.production_id else False

        self.format_id = self.product_id.format_id if self.product_id and media_id and (media_id in self.product_id.format_id.media_ids) else False
        self.location_id = self.product_id.location_id if self.product_id and media_id and (media_id in self.product_id.location_id.media_ids) else False

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return

        context_partner = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order)
        pricelist_context = dict(context_partner, uom=self.product_uom.id)

        price, rule_id = self.order_id.pricelist_id.with_context(pricelist_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        new_list_price, currency_id = self.with_context(context_partner)._get_real_price_currency(self.product_id, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
        new_list_price = self.env['account.tax']._fix_tax_included_price(new_list_price, self.product_id.taxes_id, self.tax_id)

        if new_list_price != 0:
            if self.product_id.company_id and self.order_id.pricelist_id.currency_id != self.product_id.company_id.currency_id:
                # new_list_price is in company's currency while price in pricelist currency
                new_list_price = self.env['res.currency'].browse(currency_id).with_context(context_partner).compute(new_list_price, self.order_id.pricelist_id.currency_id)
            discount_base = (new_list_price - price) / new_list_price * 100
            if discount_base > 0:
                self.discount_base = discount_base

    @api.onchange('product_id', 'production_id', 'format_id', 'location_id', 'date_start', 'date_end')
    def _compute_name(self):
        name = u''
        if self.product_id:
            name += _('Product: ') + self.product_id.name
        if self.format_id:
            name += _('\nFormat: ') + self.format_id.name
        if self.location_id:
            name += _('\nLocation: ') + self.location_id.name
        if self.production_id:
            name += _('\nProduction/Event: ') + self.production_id.name
        if self.date_start:
            name += _('\nStart: ') + datetime.datetime.strptime(self.date_start, '%Y-%m-%d').strftime('%d/%m/%Y')
        if self.date_end:
            name += _('\nEnd: ') + datetime.datetime.strptime(self.date_end, '%Y-%m-%d').strftime('%d/%m/%Y')
        self.name = name
            

    @api.one
    def _compute_sequence_computed(self):
        self.sequence_computed = 1
        for line in self.order_id.order_line:
            if line.id == self.id:
                break
            self.sequence_computed += 1

    @api.one
    def _compute_attachment_count(self):
        self.attachment_count = len(self.attachment_ids)

    @api.one
    @api.depends('production_id')
    def _compute_product_category_id(self):
        if self.production_id:
            self.product_category_id = self.production_id.production_type_id.product_category_id
        else:
            categories = self.env['product.category'].search([('parent_id', '=', False)])
            self.product_category_id = categories[0] if len(categories) >= 1 else False

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)

        vals['name'] = '\n'.join(filter(None, [
            self.name,
            _('Unit Price : ')+str(self.price_unit)+self.currency_id.symbol if self.product_uom_qty != 1 or qty != self.product_uom_qty else '',
            _('Quantity : ')+str(self.product_uom_qty) if self.product_uom_qty != 1 else '',
            _('Invoiced Percentage : ')+str(round(qty / self.product_uom_qty * 100, 2))+' %' if self.product_uom_qty != 0 and qty != self.product_uom_qty else '',
            _('Your Customer : ')+self.order_id.partner_id.name if self.order_id.partner_id != self.order_id.partner_invoice_id else '',
            _('Price : ')+str(qty*self.price_unit)+self.currency_id.symbol+(' - '+str(self.discount_base)+_(' % customer discount') if self.discount_base>0 else '')+(' = '+str(qty*self.price_unit*(1-self.discount_base/100))+self.currency_id.symbol if self.discount_base>0 and self.commission>0 else '')+(' - '+str(self.commission)+_(' % agency commission') if self.commission>0 else ''),
        ]))

        return vals

    @api.depends('qty_invoiced_confirmed', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty_confirmed(self):
        """
        Compute the quantity to invoice confirmed (if the invoices are not open or paid, they are considered to invoice).
        If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice_confirmed = line.product_uom_qty - line.qty_invoiced_confirmed
                else:
                    line.qty_to_invoice_confirmed = line.qty_delivered - line.qty_invoiced_confirmed
            else:
                line.qty_to_invoice_confirmed = 0

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_invoiced_qty_confirmed(self):
        """
        Compute the quantity invoiced confirmed (only the open & paid invoices).
        If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO and that is intentional: if
        a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
        it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
        """
        for line in self:
            qty_invoiced_confirmed = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state in ['open', 'paid']:
                    if invoice_line.invoice_id.type == 'out_invoice':
                        qty_invoiced_confirmed += invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
                    elif invoice_line.invoice_id.type == 'out_refund':
                        qty_invoiced_confirmed -= invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
            line.qty_invoiced_confirmed = qty_invoiced_confirmed

    # @api.one
    # def toggle_full_equipment_received(self):
    #     self.full_equipment_received = not self.full_equipment_received