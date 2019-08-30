# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection([
        ('prospect', _('Prospect')),
        ('customer', _('Customer')),
        ('excustomer', _('Ex-Customer'))
    ], string='Customer Status', index=True, default='prospect')

    def _check_compute_fields(self, values):
        customer = values['customer'] if 'customer' in values else self.customer

        if not customer:
            values['state'] = False
        else:
            state = values['state'] if 'state' in values else self.state

            if not state:
                values['state'] = 'prospect'

        return values

    @api.model
    def create(self, values):
        values = self._check_compute_fields(values)
        return super(ResPartner, self).create(values)

    @api.one
    def write(self, values):
        values = self._check_compute_fields(values)
        return super(ResPartner, self).write(values)
