# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    title_gender_ids = fields.Many2many(related='title.gender_ids', string="Title Gender(s)", readonly=True)

    @api.onchange('title')
    def set_gender(self):
        """ Auto set gender when only one possible. Cleanup field otherwise but leave both options possible"""
        if len(self.title_gender_ids) == 1:
            self.gender_id = self.title_gender_ids[0]
        else:
            self.gender_id = False
