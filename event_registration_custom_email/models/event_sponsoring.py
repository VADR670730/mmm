# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
from odoo import api, models, fields, _


class EventRegistrationCode(models.Model):
    _inherit = 'event.registration.code'

    send_registration_mail = fields.Boolean(string='Send email', default=False, help='Send Confirmation email on attendeed confirmation (after fully paid or code at 100% so not needed to pay)')
