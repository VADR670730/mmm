# -*- coding: utf-8 -*-

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import models, _

import logging
_logger = logging.getLogger(__name__)

class ProductionXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, wizard):
        for obj in wizard:
            #-----Create Worksheet-----
            ws = workbook.add_worksheet(_("Global Productions"))
            ws.set_column(0, 6, 30)

            #-->Define formats
            bold = workbook.add_format({'bold': True})
            bold_underline_wrap = workbook.add_format({'bold': True, 'text_wrap': True, 'underline': True})
            format_title = workbook.add_format({'bold': True, 'font_size': 12})
            total_title = workbook.add_format({'bold': True, 'font_size': 14})
            percentage = workbook.add_format({'num_format': '0.00 %'})
            rounded = workbook.add_format({'num_format': '#,##0.00'})
            bold_percentage = workbook.add_format({'num_format': '0.00 %', 'bold': True})
            green = workbook.add_format({'bg_color': 'green'})
            
            #--> Get all matching productions <--
            prods = self.env['publisher.production'].search([
                                                                ('date_closing', '>=', data['date_from']), 
                                                                ('date_closing', '<=', data['date_to'])
                                                            ])
            prods = prods.sorted(key=lambda r: r.production_type_id.id)
            if data['hide_drafts']:
                prods = prods.filtered(lambda r: r.state != 'draft')
            
            #--> Fill sheet <--
            #fill first line with titles
            titles = [_("Productions (Sequence Number)"), _("Production (Name)"), _("Expected Turnover"), _("Actual Turnover"), _("Optional Turnover"), _("Ratio (Actual/Expected)"), _("Difference (Actual-Expected)")]
            index = 0
            for title in titles:
                ws.write(0, index, title, format_title)
                index += 1
            
            #datas
            total_rows = []
            type, row, col, type_first_row = 0, 1, 0, 0
            option_expected_turnover, option_actual_turnover, option_option_turnover = 0, 0, 0
            for prod in prods:
                #If type change, put new type name between productions
                if prod.production_type_id.id != type:
                    if type_first_row:
                        #write totals except for last type
                        ws.write(row, col, _('Total Turnover'), bold)
                        ws.write_formula(row, col + 2, "=SUM(C%s:C%s)" % (type_first_row + 1, row), bold)
                        ws.write_formula(row, col + 3, "=SUM(D%s:D%s)" % (type_first_row + 1, row))
                        ws.write_formula(row, col + 4, "=SUM(E%s:E%s)" % (type_first_row + 1, row))
                        ws.write_formula(row, col + 5, "=D%s/C%s" % (row + 1, row + 1), percentage)
                        ws.write_formula(row, col + 6, "=SUM(G%s:G%s)" % (type_first_row + 1, row))
                        row += 1
                        total_rows.append("%s" % row)
                        ws.write(row, col, _("% Turnover"), bold)
                        row += 2
                        
                    #write new type
                    ws.write(row, col, prod.production_type_id.name, bold)
                    
                    #update values
                    type = prod.production_type_id.id
                    row += 1
                    type_first_row = row
                    
                                        
                #check values for option voucher
                for line in prod.sale_line_ids:
                    if line.order_id.state == 'option':
                        option_expected_turnover += prod.expected_turnover
                        option_actual_turnover += prod.actual_turnover
                        option_option_turnover += prod.potential_turnover-prod.actual_turnover
                    
                #write productions
                ws.write(row, col, prod.seq_number)
                ws.write(row, col + 1, prod.name)
                ws.write(row, col + 2, prod.expected_turnover)
                ws.write(row, col + 3, prod.actual_turnover)
                ws.write(row, col + 4, prod.potential_turnover-prod.actual_turnover)
                if prod.expected_turnover:
                    ws.write_formula(row, col + 5, "=D%s/C%s" % (row + 1, row + 1), percentage) #no *100 because of format
                else:
                    ws.write(row, col + 5, "/")
                ws.write_formula(row, col + 6, "=D%s-C%s" % (row + 1, row + 1), rounded)
                row += 1
                
            #write last type total
            ws.write(row, col, _('Total Turnover'), bold)
            ws.write(row, col + 2, "=SUM(C%s:C%s)" % (type_first_row + 1, row), bold)
            ws.write_formula(row, col + 3, "=SUM(D%s:D%s)" % (type_first_row + 1, row))
            ws.write_formula(row, col + 4, "=SUM(E%s:E%s)" % (type_first_row + 1, row))
            ws.write_formula(row, col + 5, "=D%s/C%s" % (row + 1, row + 1), percentage)
            ws.write_formula(row, col + 6, "=SUM(G%s:G%s)" % (type_first_row + 1, row))
            row += 1
            total_rows.append("%s" % row)
            ws.write(row, col, _("% Turnover"), bold)
            row += 2
            
            #write total for all productions
            ws.write(row, col, "TOTAL", total_title)
            row += 1
            ws.write(row, col, _('Total Turnover'), bold)
            ws.write_formula(row, col + 2, "=C%s" % "+C".join(total_rows), bold)
            ws.write_formula(row, col + 3, "=D%s" % "+D".join(total_rows))
            ws.write_formula(row, col + 5, "=D%s/C%s" % (row + 1, row + 1), percentage)
            ws.write_formula(row, col + 6, "=G%s" % "+G".join(total_rows))
            row += 1
            main_total_cell = "C%s" % row
            ws.write(row, col + 2, "100,00 %", bold)
            row += 2
            
            #write % CA
            col += 2
            for obj in total_rows:
                ws.write_formula(int(obj), col, "=C%s/%s" % (obj, main_total_cell), bold_percentage)
            col = 0
            
            
            #write in option voucher
            ws.write(row, col, _(u"Detail: production line waiting for signature"), bold_underline_wrap)
            ws.write(row, col + 2, option_expected_turnover)
            ws.write(row, col + 3, option_actual_turnover)
            ws.write_formula(row, col + 5, "=D%s/C%s" % (row + 1, row + 1), percentage)
            ws.write(row, col + 6, option_option_turnover)

                
ProductionXlsx('report.publisher.report_publisher_production.xlsx', 'publisher.production.wizard')
