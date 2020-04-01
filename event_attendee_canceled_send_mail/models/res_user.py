# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = 'res.users'

    send_canceled_registration = fields.Boolean(string=_("Send Email for Canceled Registration"), default=False)