# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models
from pprint import pformat
_logger = logging.getLogger(__name__)


class CreateCRMLeads(models.TransientModel):
    _name = 'partner.create.crm.leads.wizard'

    @api.model
    def default_get(self, fields):
        res = super(CreateCRMLeads, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'res.partner' and active_ids:
            res['partner_ids'] = active_ids
        return res

    prefix = fields.Char('Lead Prefix name')
    production_ids = fields.Many2many('publisher.media', string="Media")
    partner_ids = fields.Many2many('res.partner', string='Contacts')

    @api.multi
    def action_generate(self):
        if not self.partner_ids:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }

        # Create batch CRM Leads
        lead_ids = []
        note = "Generated in batch by " + self.env.user.name
        for partner in self.partner_ids:
            name = partner.name
            if self.prefix:
                name = self.prefix + " : " + name
            name += " - "
            name += ",".join([media.name for media in self.production_ids])
            lead_id = self.env['crm.lead'].create({
                'name': name,
                'partner_id': partner.id,
                'production_id': self.production_ids or False,
                'description': note,
            })
            lead_ids.append(lead_id.id)

        action = self.env.ref('crm.crm_lead_opportunities').read()[0]
        if len(lead_ids) > 1:
            action['domain'] = [('id', 'in', lead_ids)]
        elif len(lead_ids) == 1:
            action['views'] = [(self.env.ref('crm.crm_case_form_view_oppor').id, 'form')]
            action['res_id'] = lead_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
