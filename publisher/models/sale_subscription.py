# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    partner_id = fields.Many2one('res.partner', string="Invoice Address")
    partner_customer_id = fields.Many2one('res.partner', string="Customer")
    free_subscription = fields.Boolean(string="Is a Free Subscription", default=False)

    @api.multi
    def _prepare_invoice_line(self, line, fiscal_position):
        vals = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position)

        vals['name'] = '\n'.join(filter(None, [
            line.name,
            _('Customer : ')+self.partner_customer_id.name if self.partner_customer_id else '',
            _('Shipping Address : ')+', '.join(filter(None, [
                line.partner_shipping_id.name or '',
                line.partner_shipping_id.street or '',
                line.partner_shipping_id.street2 or '',
                line.partner_shipping_id.city or '',
                line.partner_shipping_id.state_id.name or '',
                line.partner_shipping_id.zip or '',
                line.partner_shipping_id.country_id.name or '',
            ])) if line.partner_shipping_id else '',
            _('Subscription Reference : ')+self.name,
            _('Language : ')+line.language_id.name if line.language_id else '',
            _('Unit Price : ')+str(line.price_unit)+self.currency_id.symbol if line.quantity != 1 else '',
            _('Quantity : ')+str(line.quantity) if line.quantity != 1 else '',
            _('Price : ')+str(line.quantity*line.price_unit)+self.currency_id.symbol+(' - '+str(line.discount)+_(' % customer discount') if line.discount>0 else ''),
        ]))

        return vals

    @api.returns('account.invoice')
    def _recurring_create_invoice(self, automatic=False):
        AccountInvoice = self.env['account.invoice']
        invoices = []
        current_date = fields.Date.today()
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        domain = [('id', 'in', self.ids)] if self.ids else [('recurring_next_date', '<=', current_date), ('state', '=', 'open')]
        domain.append(('free_subscription', '!=', True))
        sub_data = self.search_read(fields=['id', 'company_id'], domain=domain)
        for company_id in set(data['company_id'][0] for data in sub_data):
            sub_ids = map(lambda s: s['id'], filter(lambda s: s['company_id'][0] == company_id, sub_data))
            subs = self.with_context(company_id=company_id, force_company=company_id).browse(sub_ids)
            for sub in subs:
                try:
                    invoices.append(AccountInvoice.create(sub._prepare_invoice()))
                    invoices[-1].message_post_with_view('mail.message_origin_link',
                     values={'self': invoices[-1], 'origin': sub},
                     subtype_id=self.env.ref('mail.mt_note').id)
                    invoices[-1].compute_taxes()
                    next_date = fields.Date.from_string(sub.recurring_next_date or current_date)
                    rule, interval = sub.recurring_rule_type, sub.recurring_interval
                    new_date = next_date + relativedelta(**{periods[rule]: interval})
                    sub.write({'recurring_next_date': new_date})
                    if automatic:
                        self.env.cr.commit()
                except Exception:
                    if automatic:
                        self.env.cr.rollback()
                        _logger.exception('Fail to create recurring invoice for subscription %s', sub.code)
                    else:
                        raise
        return invoices

    @api.multi
    def set_open(self):
        return self.write({'state': 'open'})

    @api.multi
    def set_close(self):
        return self.write({'state': 'close'})
