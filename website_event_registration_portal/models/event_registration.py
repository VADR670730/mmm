# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import uuid
import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    portal_update_token = fields.Char(default=lambda x: str(uuid.uuid4()).upper())
    is_anonymized = fields.Boolean(string="Anonymized", default=False)
