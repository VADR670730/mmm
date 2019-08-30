# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import uuid
import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class EventRegistrationCode(models.Model):
    _inherit = 'event.registration.code'

    allow_registration_change = fields.Boolean(default=False)
