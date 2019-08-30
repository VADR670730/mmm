# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProjectTemplate(models.Model):
    _name = 'publisher.project.template'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)
    active = fields.Boolean(string='Is Active', copy=False, default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)
    stage_ids = fields.Many2many('project.task.type', string="Stages")
    is_default_template = fields.Boolean(string="Is Default Template")
    is_production_template = fields.Boolean(string="Is Production Template")

    @api.model
    def get_project_stages(self, domain):
        templates = self.env['publisher.project.template'].search(domain)

        if len(templates) > 0:
            return templates[0].stage_ids.ids

        return False

    @api.model
    def create_project(self, domain, values):
        stage_ids = self.get_project_stages(domain)

        if stage_ids:
            values['type_ids'] = [(4, stage_id) for stage_id in stage_ids]

        return self.env['project.project'].create(values)