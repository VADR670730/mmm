# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # address formatting
    country_zip_city = fields.Char(compute='_compute_country_zip_city')

    @api.multi
    @api.depends('country_id', 'zip', 'city')
    def _compute_country_zip_city(self):
        for partner in self:
            partner.country_zip_city = u"{}-{} {}".format(
                partner.country_id.name.upper()[0] if partner.country_id else '',
                partner.zip if partner.zip else '',
                partner.city.upper() if partner.city else '')

    @api.model
    def _address_fields(self):
        address_fields = super(ResPartner, self)._address_fields()
        address_fields.append('country_zip_city')
        return address_fields
