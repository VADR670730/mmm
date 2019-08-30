# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    client_ref = fields.Char(string='Customer Reference')
    final_customer_id = fields.Many2one('res.partner', string="Final Customer")

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'publisher.report_invoice_publisher')


class AccountInvoiceReport(models.AbstractModel):
    _name = 'report.publisher.report_invoice_publisher'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_invoice_publisher')
        docargs = {
            'header_prefix': _(""),
            'header_title1_1': _("Invoice"),
            'header_title1_2': _("PRO-FORMA"),
            'header_title1_3': _("Draft Invoice"),
            'header_title1_4': _("Cancelled Invoice"),
            'header_title1_5': _("Refund"),
            'header_title1_6': _("Vendor Refund"),
            'header_title1_7': _("Vendor Bill"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['account.invoice'].search([('id', 'in', docids)])
        }

        return report_obj.render('publisher.report_invoice_publisher', docargs)


class AccountInvoiceDuplicateReport(models.AbstractModel):
    _name = 'report.publisher.report_invoice_publisher_duplicate'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_invoice_publisher_duplicate')
        docargs = {
            'header_prefix': _("Duplicate "),
            'header_title1_1': _("Invoice"),
            'header_title1_2': _("PRO-FORMA"),
            'header_title1_3': _("Draft Invoice"),
            'header_title1_4': _("Cancelled Invoice"),
            'header_title1_5': _("Refund"),
            'header_title1_6': _("Vendor Refund"),
            'header_title1_7': _("Vendor Bill"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['account.invoice'].search([('id', 'in', docids)])
        }

        return report_obj.render('publisher.report_invoice_publisher_duplicate', docargs)