# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class IrFilters(models.Model):
    _inherit = 'ir.filters'

    @api.model
    def create(self, vals):
        if not vals.get('user_id') and not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessError(_('You are not allowed to create a shared filter. Only personal filters are allowed.'))
            return False

        return super(IrFilters, self).create(vals)