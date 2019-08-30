# -*- coding: utf-8 -*-

from odoo import fields, models, api
import re

import logging
_logger = logging.getLogger(__name__)


class ResCountry(models.Model):
    """Override default adresses formatting of countries"""
    _inherit = 'res.country'

    address_format = fields.Text(
        default=(
            "%(street)s\n%(street2)s\n"
            "%(country_zip_city)s\n"
        )
    )

    @api.multi
    def get_address_fields(self):
        self.ensure_one()
        fields = re.findall(r'\((.+?)\)', self.address_format)
        if 'country_zip_city' in fields:
            #s.remove('country_zip_city')
            fields.append('country_name')
            fields.append('zip')
            fields.append('city')
        return fields
            
