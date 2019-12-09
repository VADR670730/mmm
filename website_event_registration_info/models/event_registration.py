# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class EventRegistrationMoreInfo(models.Model):
    _inherit = 'event.registration'

    last_name = fields.Char()
    function = fields.Char()
    company = fields.Char()
    lang_id = fields.Many2one('res.lang', 'Language')
    poll_url = fields.Char()
    poll_code = fields.Char()

    # Order registration by 'lower' values
    @api.model
    def _generate_order_by(self, order_spec, query):
        """
                Attempt to construct an appropriate ORDER BY clause based on order_spec, which must be
                a comma-separated list of valid field names, optionally followed by an ASC or DESC direction.
                :raise ValueError in case order_spec is malformed
                """
        order_by_clause = ''
        order_spec = order_spec or self._order
        if order_spec:
            order_by_elements = self._generate_order_by_inner(self._table, order_spec, query)
            if order_by_elements:
                res = order_by_elements
                for i, el in enumerate(res):
                    order_list = el.split(' ')
                    if "date" not in el and order_list and order_list[0] == 'name':
                        order_by_elements[i] = "LOWER(" + order_list[0] + ") " + order_list[1] if len(order_list) > 1 else "LOWER(" + order_list[0] + ")"
                order_by_clause = ",".join(order_by_elements)

        return order_by_clause and (' ORDER BY %s ' % order_by_clause) or ''
