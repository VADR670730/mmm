# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    mmm_new = fields.Boolean(string="Is new")

    mmm_sub_be_l2f = fields.Char(string="Sub link2fleet")
    mmm_sub_be_l2ffree = fields.Char(string="Sub link2fleet gratuit")
    mmm_sub_lux_guide = fields.Char(string="Sub Guide")
    mmm_sub_lux_print = fields.Char(string="Sub Print")

    @api.multi
    def compute_mmm(self):
        partners = self.env['res.partner'].search([('mmm_new', u'=', True), '|', '|', '|', ('mmm_sub_lux_guide', '!=', False), ('mmm_sub_lux_print', '!=', False), ('mmm_sub_be_l2f', '!=', False), ('mmm_sub_be_l2ffree', '!=', False)], limit=200)

        for partner in partners:
            _logger.debug("Partner: %s", partner.name)

            subs = []

            if partner.mmm_sub_be_l2f:
                subs.append({
                    'template': 'link2fleet',
                    'language': partner.mmm_sub_be_l2f,
                    'free': False,
                    'company': 'be'
                })
            if partner.mmm_sub_be_l2ffree:
                subs.append({
                    'template': 'link2fleet',
                    'language': partner.mmm_sub_be_l2ffree,
                    'free': True,
                    'company': 'be'
                })
            if partner.mmm_sub_lux_guide:
                subs.append({
                    'template': 'Guide',
                    'language': partner.mmm_sub_lux_guide,
                    'free': True,
                    'company': 'lu'
                })
            if partner.mmm_sub_lux_print:
                subs.append({
                    'template': 'Print',
                    'language': partner.mmm_sub_lux_print,
                    'free': True,
                    'company': 'lu'
                })

            for sub in subs:

                def getObject(model, map, key):
                    return self.env[model].search([('name', '=', map[key])])


                template = self.env['sale.subscription.template'].search([('name', '=', sub['template'])])

                sub_id = self.env['sale.subscription'].create({
                    'partner_id': partner.id,
                    'pricelist_id': partner.property_product_pricelist.id,
                    'partner_customer_id': partner.id,
                    'template_id': template.id,
                    'free_subscription': sub['free'],
                    'company_id': getObject(
                        'res.company',
                        {
                            'be': 'link2fleet Belgium',
                            'lu': 'link2fleet Luxembourg'
                        },
                        sub['company']
                    ).id
                })

                for line in template.subscription_template_line_ids:
                    line_id = self.env['sale.subscription.line'].create({
                        'analytic_account_id': sub_id.id,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'sold_quantity': line.quantity,
                        'uom_id': line.uom_id.id,
                        'price_unit': line.price,
                        'partner_shipping_id': partner.id,
                        'language_id': getObject(
                            'res.lang',
                            {
                                'EN': 'English',
                                'FR': 'French (BE) / Français (BE)',
                                'NL': 'Dutch (BE) / Nederlands (BE)'
                            },
                            sub['language']
                        ).id
                    })

                    line_id.onchange_product_id()
                    line_id._compute_quantity()
                    line_id._compute_price_subtotal()

                sub_id.onchange_partner_id()
                sub_id.on_change_template()
                sub_id._compute_recurring_total()

            partner.mmm_new = False;

        return False