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
