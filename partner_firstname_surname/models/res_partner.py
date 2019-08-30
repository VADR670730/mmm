# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    firstname = fields.Char(string="Firstname")
    surname = fields.Char(string="Surname")
    computed_name = fields.Char(related='name')

    @api.multi
    @api.onchange('firstname', 'surname')
    def onchange_firstname_lastname(self):
        self.update({
            'name': self.firstname + ' ' + self.surname if self.firstname and self.surname else ''
        })