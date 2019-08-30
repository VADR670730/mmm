# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agency_id = fields.Many2one('res.partner', string="Agency")
    reference = fields.Char(string='Internal Reference')
    link_agency = fields.Boolean(string='Sell via an agency', default=False)
    sale_order_mode = fields.Selection([('customer_alone', 'Customer alone'), ('customer_agency', 'Customer via agency'), ('agency', 'Agency alone')])
    # has_production = fields.Boolean(string='Has Production', compute='_compute_has_production')
    production_names = fields.Char(string="Productions", compute='_compute_production_names')

    @api.multi
    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        return {}

    @api.multi
    @api.onchange('partner_id', 'agency_id')
    def onchange_partner_invoice_id(self):
        """
        Trigger the change of fiscal position when the invoice address is modified.
        """

        partner_to_use = self.agency_id if self.agency_id else self.partner_id

        self.update({
            'pricelist_id': partner_to_use.property_product_pricelist and partner_to_use.property_product_pricelist.id or False,
            'payment_term_id': partner_to_use.property_payment_term_id and partner_to_use.property_payment_term_id.id or False,
            'fiscal_position_id': self.env['account.fiscal.position'].get_fiscal_position(partner_to_use.id, partner_to_use.id)
        })

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the invoice address when the partner is changed.
        """

        res = super(SaleOrder, self).onchange_partner_id()

        if self.agency_id:
            self.update({
                'partner_invoice_id': self.agency_id.address_get(['invoice'])['invoice']
            })
        else:
            self.update({
                'partner_invoice_id': self.partner_id.address_get(['invoice'])['invoice']
            })

    @api.multi
    @api.onchange('agency_id')
    def onchange_agency_id(self):
        """
        Update the invoice address when the agency is changed.
        """

        if self.agency_id:
            addr =  self.agency_id.address_get(['invoice'])['invoice']
        elif self.partner_id:
            addr =  self.partner_id.address_get(['invoice'])['invoice']
        else:
            addr = False

        self.update({
            'partner_invoice_id': addr
        })

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'publisher.report_saleorder_publisher')

    @api.multi
    def print_quotation_noprice(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'publisher.report_saleorder_publisher_noprice')

    @api.multi
    def write(self, vals):
        response = super(SaleOrder, self).write(vals)

        if response:
            if vals.get('state'):
                for line in self.order_line:
                    if not line._check_publisher_fields({}):
                        self.state = 'draft'
                        break

        return response

    @api.model
    def create(self, vals):
        response = super(SaleOrder, self).create(vals)

        if response:
            if vals.get('state'):
                self = self.env['sale.order'].search([('id', '=', response.id)])
                for line in self.order_line:
                    if not line._check_publisher_fields({}):
                        self.state = 'draft'
                        break

        return response

    # @api.one
    # @api.depends('order_line')
    # def _compute_has_production(self):
    #     self.has_production = False
    #     for line in self.order_line:
    #         if line.production_id:
    #             self.has_production = True
    #             break;

    @api.multi
    @api.depends('order_line')
    def _compute_production_names(self):
        for order in self:
            name = ''
            if len(order.order_line) == 1:
                name = order.order_line[0].production_id.name
            if len(order.order_line) > 1:
                for line in order.order_line:
                    name = name + line.production_id.name + ', '
            order.production_names = name

            
class SaleOrderReport(models.AbstractModel):
    _name = 'report.publisher.report_saleorder_publisher'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_saleorder_publisher')
        docargs = {
            'header_title1_1': _("Order"),
            'header_title1_2': _("Quotation"),
            'header_title1_3': _("Order Confirmation"),
            'header_title1_4': _("Sales Order"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['sale.order'].search([('id', 'in', docids)])
        }

        return report_obj.render('publisher.report_saleorder_publisher', docargs)


class SaleOrderReportNoPrice(models.AbstractModel):
    _name = 'report.publisher.report_saleorder_publisher_noprice'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_saleorder_publisher')
        docargs = {
            'header_title1_1': _("Order"),
            'header_title1_2': _("Quotation"),
            'header_title1_3': _("Order Confirmation"),
            'header_title1_4': _("Sales Order"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['sale.order'].search([('id', 'in', docids)]),
            'no_price': True
        }

        return report_obj.render('publisher.report_saleorder_publisher', docargs)

class SaleOrderReportFinal(models.AbstractModel):
    _name = 'report.publisher.report_saleorder_publisher_final'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_saleorder_publisher')
        docargs = {
            'header_title1_1': _("Order"),
            'header_title1_2': _("Quotation"),
            'header_title1_3': _("Order Confirmation"),
            'header_title1_4': _("Sales Order"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['sale.order'].search([('id', 'in', docids)]),
            'final': True
        }

        return report_obj.render('publisher.report_saleorder_publisher', docargs)