# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from itertools import groupby
from pprint import pformat
import logging
_logger = logging.getLogger(__name__)
import tempfile
import zipfile
import base64
import urllib

import datetime

class Production(models.Model):
    _name = 'publisher.production'
    _inherit = 'mail.thread'
    _order = 'name'
    _sql_constraints = [(
        'seq_number_unique', 
        'unique(seq_number)',
        _('This sequence number is already taken')
    )]

    name = fields.Char(string='Name', index=True, required=True, readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('archived', 'Archived')
        ], string='State', default='draft', required=True, track_visibility='always')
    production_type_id = fields.Many2one('publisher.production.type', string='Production Type', required=True, readonly=True, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('project.project', string="Project", track_visibility='always')
    date_start = fields.Date(string='Publication Date / Event', required=True, readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
    date_end = fields.Date(string='End Date', readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
    date_closing = fields.Date(string='Closing Date', readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
    date_full_equipment_limit = fields.Date(string='Full Equipment Limit Date', readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
    sale_line_all_ids = fields.One2many('sale.order.line', 'production_id', string='All Production Lines')
    sale_line_ids = fields.One2many('sale.order.line', 'production_id', string='Production Lines', domain=[('state', 'in', ['option', 'sale', 'done'])])
    expected_turnover = fields.Monetary(string="Expected Turnover", readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
    invoicing_mode = fields.Selection([
        ('before', 'Before Publication'),
        ('after', 'After Publication'),
        ('both', 'Before & After Publication')
        ], string='Invoicing Mode', default='before', required=True, readonly=True, states={'draft': [('readonly', False)], 'confirmed':[('readonly', False)]})
    down_payment = fields.Float(string='Down Payment', default=0, readonly=True, states={'draft': [('readonly', False)],'confirmed':[('readonly', False)]})
    seq_number = fields.Char(string="Sequence Number", required=True, readonly=True, copy=False, track_visibility='always', states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    date_blanco = fields.Date(string='Blanco Date', readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
    note = fields.Text(string="Notes")
    themes = fields.Char(string="Production Themes", readonly=True, track_visibility='always', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})

    sale_lines_count = fields.Integer(string="Production Lines Count", compute='_compute_sale_lines_count')
    sale_lines_confirmed_count = fields.Char(string="Confirmed Lines", compute='_compute_sale_lines_confirmed_count')
    sale_lines_full_equipment_count = fields.Char(string="Equip. Received Lines", compute='_compute_sale_lines_full_equipment_count')
    potential_turnover = fields.Monetary(string="Potential Turnover", compute='_compute_potential_turnover', store=True)
    actual_turnover = fields.Monetary(string="Actual Turnover", compute='_compute_actual_turnover', store=True)
    turnover_delta = fields.Monetary(string='Diff. Actual / Expected Turnover', compute='_compute_turnover_delta', store=True)
    turnover_delta_sign = fields.Char(string='Turnover Delta Sign', compute='_compute_turnover_delta_sign')

    export_file = fields.Binary(attachment=True, help="This field holds the attachments export file.", readonly=True)
    sale_ids = fields.Many2many('sale.order', string="Sales", compute='_compute_sale_ids')
    invoice_ids = fields.Many2many('account.invoice', string="Invoices", compute='_compute_invoice_ids')
    invoice_count = fields.Integer(string="Invoice Count", compute='_compute_invoice_count')
    invoice_status = fields.Selection([
        ('no', 'Nothing to Invoice'),
        ('to invoice', 'To Invoice')
    ], string="Invoice Status", compute='_compute_invoice_status')
    calendar_view = fields.Boolean(string="Allow Calendar View", compute='_compute_calendar_view')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('publisher.production'), states={'draft': [('readonly', False)]})

    purchase_order_line_ids = fields.One2many('purchase.order.line', 'production_id', string='Pruchase Lines')
    purchase_total = fields.Monetary(string="Purchase Total", compute='_compute_purchase_total', store=True)
    purchase_invoice_ids = fields.Many2many('account.invoice', string="Invoices", compute='_compute_purchase_invoice_ids')
    purchase_invoice_count = fields.Integer(string="Invoice Count", compute='_compute_purchase_invoice_count')

    crm_lead_ids = fields.Many2many('crm.lead', compute='_compute_crm_lead_count', string='CRM Leads')
    crm_lead_count = fields.Integer(string="Lead Count", compute='_compute_crm_lead_count')

    @api.one
    def _compute_sale_lines_count(self):
        self.sale_lines_count = len(self.sale_line_ids)

    @api.one
    def name_get(self):
        return (self.id, '[' + self.seq_number + '] ' + self.name)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            args = args or []
            args.extend(['|', ('seq_number', operator, name), ('name', operator, name)])
            return self.search(args, limit=limit).name_get()

        return super(Production, self).name_search(name, args=args, operator=operator, limit=limit)


    @api.model
    def create(self, vals):
        production_type_id = self.env['publisher.production.type'].search([('id', '=', vals['production_type_id'])])
        if vals.get('seq_number', _('New')) == _('New'):
            vals['seq_number'] = production_type_id.sequence_id.next_by_id() or _('New')

        return super(Production, self).create(vals)


    @api.one
    def _compute_sale_lines_confirmed_count(self):
        count = 0
        for line in self.sale_line_ids:
            if line.order_id.state in ['sale', 'done']:
                count += 1

        self.sale_lines_confirmed_count = str(count) + '/' + str(len(self.sale_line_ids))


    @api.one
    def _compute_sale_lines_full_equipment_count(self):
        count = 0
        confirmed_count = 0
        for line in self.sale_line_ids:
            if line.order_id.state in ['sale', 'done']:
                confirmed_count += 1
                if line.full_equipment_received:
                    count += 1

        self.sale_lines_full_equipment_count = str(count) + '/' + str(confirmed_count)


    @api.one
    @api.depends('sale_line_ids', 'sale_line_ids.price_subtotal', 'sale_line_ids.order_id.state')
    def _compute_potential_turnover(self):
        self.potential_turnover = sum([line.price_subtotal for line in self.sale_line_ids])


    @api.one
    @api.depends('sale_line_ids', 'sale_line_ids.price_subtotal', 'sale_line_ids.order_id.state')
    def _compute_actual_turnover(self):
        self.actual_turnover = 0
        for line in self.sale_line_ids:
            if line.order_id.state in ['sale', 'done']:
                self.actual_turnover += line.price_subtotal


    @api.one
    @api.depends('expected_turnover', 'actual_turnover')
    def _compute_turnover_delta(self):
        self.turnover_delta = self.actual_turnover - self.expected_turnover


    @api.one
    def _compute_turnover_delta_sign(self):
        self.turnover_delta_sign = '+' if self.turnover_delta > 0 else ''

    @api.one
    def _compute_sale_ids(self):
        sale_ids_id = []
        for line in self.sale_line_ids:
            if line.order_id.id not in sale_ids_id:
                sale_ids_id.append(line.order_id.id)
        self.sale_ids = self.env['sale.order'].search([('id', 'in', sale_ids_id)])

    @api.one
    def _compute_invoice_ids(self):
        invoice_ids_id = []
        # Add invoices that are linked to the sale order lines
        for line in self.sale_line_ids:
            for invoice_line in line.invoice_lines:
                if not invoice_line.invoice_id.id in invoice_ids_id:
                    invoice_ids_id.append(invoice_line.invoice_id.id)
        # Add invoices that have invoice lines linked to this production
        refund_line_ids = self.env['account.invoice.line'].search([('production_id', '=', self.id)])
        for line in refund_line_ids:
            invoice_ids_id.append(line.invoice_id.id)
        self.invoice_ids = self.env['account.invoice'].search([('id', 'in', invoice_ids_id)])

    @api.one
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        self.invoice_count = len(self.invoice_ids)

    @api.one
    def _compute_purchase_invoice_ids(self):
        invoice_ids_id = []
        for line in self.purchase_order_line_ids:
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.id not in invoice_ids_id:
                    invoice_ids_id.append(invoice_line.invoice_id.id)
        self.purchase_invoice_ids = self.env['account.invoice'].search([('id', 'in', invoice_ids_id)])

    @api.one
    @api.depends('purchase_invoice_ids')
    def _compute_purchase_invoice_count(self):
        self.purchase_invoice_count = len(self.purchase_invoice_ids)

    @api.multi
    @api.depends('crm_lead_ids')
    def _compute_crm_lead_count(self):
        for production in self:
            production.crm_lead_ids |= self.env['crm.lead'].search([('production_id', 'in', production.id)])
            production.crm_lead_count = len(production.crm_lead_ids)

    @api.one
    @api.depends('sale_line_ids')
    def _compute_invoice_status(self):
        if self.state in ['confirmed', 'done']:
            for line in self.sale_line_ids:
                if line.invoice_status == 'to invoice':
                    self.invoice_status = 'to invoice'
                    return
        self.invoice_status = 'no'

    @api.one
    def _compute_calendar_view(self):
        self.calendar_view = self.production_type_id and self.production_type_id.media_id.date_start_needed and self.production_type_id.media_id.date_end_needed

    @api.one
    def action_create_project(self):
        self.project_id = self.env['publisher.project.template'].create_project(
            [('is_production_template', '=', True)],
            {
                'name': self.name,
                'production_id': self.id
            }
        )

    @api.one
    @api.depends('purchase_order_line_ids')
    def _compute_purchase_total(self):
        self.purchase_total = sum([line.price_total for line in self.purchase_order_line_ids])

    @api.multi
    def action_view_sale_order_line(self):
        lines = self.mapped('sale_line_ids')
        action = self.env.ref('publisher.product_template_sale_order_line_action').read()[0]
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif len(lines) == 1:
            action['views'] = [(self.env.ref('view_publisher_production_line_form').id, 'form')]
            action['res_id'] = lines.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_purchase_invoice(self):
        invoices = self.mapped('purchase_invoice_ids')
        action = self.env.ref('account.action_invoice_tree2').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_crm_leads(self):
        leads = self.mapped('crm_lead_ids')
        action = self.env.ref('crm.crm_lead_opportunities').read()[0]
        if len(leads) > 1:
            action['domain'] = [('id', 'in', leads.ids)]
        elif len(leads) == 1:
            action['views'] = [(self.env.ref('crm.crm_case_form_view_oppor').id, 'form')]
            action['res_id'] = leads.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    @api.onchange('production_type_id')
    def onchange_production_type_id(self):
        for production in self:
            production.invoicing_mode = production.production_type_id.invoicing_mode
            production.down_payment = production.production_type_id.down_payment

    @api.one
    def write(self, values):
        # Forbit reset to draft when there are already sale lines
        if values.get('state') and values['state'] == 'draft' and len(self.sale_line_all_ids) > 0:
            sales = []
            for line in self.sale_line_all_ids:
                if line.order_id not in sales:
                    sales.append(line.order_id)

            raise exceptions.ValidationError(_("Production can't be set to draft if sale lines are still linked (in ") + ', '.join(sale.name for sale in sales) + ").")
            return False

        # Create a project when confirming the production
        if (values.get('state') and values['state'] == 'confirmed') and ('project_id' not in values and self.production_type_id.project_template_id):
            new_project_id = self.production_type_id.project_template_id.copy({
                'name': self.name,
                'is_template': False,
            })
            values.update({
                'project_id': new_project_id.id,
            })

        return super(Production, self).write(values)

    @api.multi
    def order_lines_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.sale_line_ids, lambda l: l.layout_category_id):
            # If last added category induced a pagebreak, this one will be on a new page
            if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
                report_pages.append([])
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or _('Uncategorized'),
                'subtotal': category and category.subtotal,
                'pagebreak': category and category.pagebreak,
                'lines': list(lines)
            })

        return report_pages

    @api.multi
    def print_production(self):
        return self.env['report'].get_action(self, 'publisher.report_production_template')

    @api.multi
    def print_production_invoice_status(self):
        return self.env['report'].get_action(self, 'publisher.report_production_invoice_status_template')

    @api.model
    def get_valid_filename(self, string):
        remove_illegals_map = dict((ord(char), None) for char in '\/*?:"<>|')
        return string.translate(remove_illegals_map)

    @api.model
    def append_attachments(self, zip_file_object, prefix = ''):
        temp_file = tempfile.mktemp(suffix='')

        existing_folders = {}

        for line in self.sale_line_ids:

            base_folder_name = prefix + self.get_valid_filename(line.order_id.partner_id.name + " - " + line.product_id.name + " (" + line.order_id.name + " #" + str(line.sequence_computed) + ")")

            folder_name = base_folder_name
            counter = 1
            while folder_name in existing_folders:
                counter += 1
                folder_name = base_folder_name + " - " + str(counter)

            existing_folders[folder_name] = True

            for f in line.attachment_ids:
                fn = open(temp_file, 'w')
                fn.write(base64.b64decode(f.datas))
                fn.close()
                zip_file_object.write(temp_file, folder_name+"/"+f.name)

    @api.multi
    def download_attachments(self):
        self.ensure_one()

        temp_zip = tempfile.mktemp(suffix='.zip')
        zip_file_object = zipfile.ZipFile(temp_zip, "w")

        self.append_attachments(zip_file_object)

        zip_file_object.close()

        fn = open(temp_zip, 'r')
        self.export_file = base64.encodestring(fn.read())
        fn.close()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?' + urllib.urlencode({
                'model': 'publisher.production',
                'field': 'export_file',
                'id': self.id,
                'filename': self.get_valid_filename(self.name) + _(" (Attachments).zip")
            }),
            'target': 'blank',
        }

    @api.multi
    def download_attachments_project(self):
        self.ensure_one()

        temp_zip = tempfile.mktemp(suffix='.zip')
        zip_file_object = zipfile.ZipFile(temp_zip, "w")

        self.append_attachments(zip_file_object, _('Production/'))
        self.project_id.append_attachments(zip_file_object, _('Project/'))

        zip_file_object.close()

        fn = open(temp_zip, 'r')
        self.export_file = base64.encodestring(fn.read())
        fn.close()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?' + urllib.urlencode({
                'model': 'publisher.production',
                'field': 'export_file',
                'id': self.id,
                'filename': self.get_valid_filename(self.name) + _(" & Project") + _(" (Attachments).zip")
            }),
            'target': 'blank',
        }



    @api.multi
    def create_invoices(self):
        self.ensure_one()

        # Extract every sale to invoice & associate lines
        sale_map = {}
        for line in self.sale_line_ids:
            if line.invoice_status == 'to invoice':
                if not line.order_id.id in sale_map:
                    sale_map[line.order_id.id] = [line]
                else:
                    sale_map[line.order_id.id].append(line)

        company_id = self.company_id
        account_journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        now = datetime.datetime.now()

        if not account_journal_id:
            raise exceptions.UserError(_('Please define an accounting sale journal for this company.'))

        invoice_ids = []

        # browse every sale to invoice
        for sale_id_id in sale_map:
            
            lines = sale_map[sale_id_id]
            sale_id = lines[0].order_id
            partner_invoice_id = sale_id.partner_invoice_id

            invoice_id = False

            # browse every line to invoice
            for line in lines:

                def get_invoice_quantity(self, line):

                    def get_ratio_to_be_invoiced(self):
                        if now < datetime.datetime.strptime(self.date_start, '%Y-%m-%d'):
                            if self.invoicing_mode == 'after':
                                return False
                            elif self.invoicing_mode == 'both':
                                if self.down_payment:
                                    return self.down_payment / 100.0
                                return False
                        return 1.0

                    ratio = get_ratio_to_be_invoiced(self)

                    if not ratio:
                        return False

                    invoice_quantity = line.product_uom_qty * ratio - line.qty_invoiced

                    if invoice_quantity <= 0.0:
                        return False

                    return invoice_quantity

                quantity = get_invoice_quantity(self, line)

                # if there is something to invoice
                if quantity:

                    # if invoice does not exist yet
                    if not invoice_id:
                        invoice_id = self.env['account.invoice'].create({
                            'origin' : sale_id.name,
                            'type': 'out_invoice',
                            'company_id' : company_id.id,
                            'currency_id' : self.currency_id.id,
                            'journal_id' : account_journal_id,
                            'partner_id' : partner_invoice_id.id,
                            'final_customer_id' : sale_id.partner_id.id,
                            'client_ref' : sale_id.client_order_ref,
                            'reference' : sale_id.reference,
                            #'date_invoice' : now.strftime('%Y-%m-%d'),
                            'state' : 'draft',
                            'reference_type' : 'none',
                            'fiscal_position_id' : partner_invoice_id.property_account_position_id.id or sale_id.fiscal_position_id.id,
                            'payment_term_id' : sale_id.payment_term_id.id,
                            'account_id' : partner_invoice_id.property_account_receivable_id.id,
                            'user_id': sale_id.user_id and sale_id.user_id.id,
                            'team_id': sale_id.team_id.id,
                            'comment' : sale_id.note
                        })
                        invoice_ids.append(invoice_id.id)

                    description = '\n'.join(filter(None, [
                        line.name,
                        _('Unit Price : ')+str(line.price_unit)+self.currency_id.symbol if line.product_uom_qty != 1 or quantity != line.product_uom_qty else '',
                        _('Quantity : ')+str(line.product_uom_qty) if line.product_uom_qty != 1 else '',
                        _('Invoiced Percentage : ')+str(round(quantity / line.product_uom_qty * 100, 2))+' %' if quantity != line.product_uom_qty else '',
                        _('Your Customer : ')+sale_id.partner_id.name if sale_id.agency_id else '',
                        _('Price : ')+str(quantity*line.price_unit)+self.currency_id.symbol+(' - '+str(line.discount_base)+_(' % customer discount') if line.discount_base>0 else '')+(' = '+str(quantity*line.price_unit*(1-line.discount_base/100))+self.currency_id.symbol if line.discount_base>0 and line.commission>0 else '')+(' - '+str(line.commission)+_(' % agency commission') if line.commission>0 else ''),
                    ]))

                    account_line = line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id
                    if not account_line:
                        raise exceptions.UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                            (line.product_id.name, line.product_id.id, line.product_id.categ_id.name))

                    fpos = sale_id.fiscal_position_id or sale_id.partner_id.property_account_position_id
                    if fpos:
                        account_line = fpos.map_account(account_line)

                    invoice_line_id = self.env['account.invoice.line'].create({
                        'invoice_id' : invoice_id.id,
                        'product_id' : line.product_id.id or False,
                        'name' : description,
                        'quantity' : quantity,
                        'price_unit' : line.price_unit,
                        'discount' : line.discount,
                        'account_id' : partner_invoice_id.property_account_receivable_id.id,
                        'sale_line_ids': [(4, [line.id])],
                        'origin' : sale_id.name,
                        'account_id' : account_line.id,
                        'uom_id': line.product_uom.id,
                        'layout_category_id': line.layout_category_id and line.layout_category_id.id or False,
                        'invoice_line_tax_ids': [(6, 0, line.tax_id.ids)],
                        'account_analytic_id': sale_id.project_id.id,
                        'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                    })

            if invoice_id:
                invoice_id.compute_taxes()

        if not invoice_ids:
            raise exceptions.ValidationError(_('Not any line to invoice, make sure the sale orders are confirmed and the production publication date / invoicing mode are ok.'))
            return False

        action = self.env.ref('account.action_invoice_tree1').read()[0]

        if len(invoice_ids) > 1:
            action['domain'] = [('id', 'in', invoice_ids)]
        else:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoice_ids[0]

        return action



class ProductionReport(models.AbstractModel):
    _name = 'report.publisher.report_production_template'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_production_template')
        docargs = {
            'header_title2': _("Global Status"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['publisher.production'].search([('id', 'in', docids)])
        }

        return report_obj.render('publisher.report_production_template', docargs)

class ProductionInvoiceStatusReport(models.AbstractModel):
    _name = 'report.publisher.report_production_invoice_status_template'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_production_invoice_status_template')
        docargs = {
            'header_title2': _("Invoice Status"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['publisher.production'].search([('id', 'in', docids)])
        }

        return report_obj.render('publisher.report_production_invoice_status_template', docargs)
