# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, exceptions, _
from pprint import pformat
_logger = logging.getLogger(__name__)


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    production_id = fields.Many2many('publisher.media', string="Media")

    @api.model
    def create(self, values):
        res = super(CRMLead, self).create(values)

        if values.get('production_id'):
            res.production_id = values.pop('production_id')

        return res
