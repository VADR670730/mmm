# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    is_registration_mail_sent = fields.Boolean(default=False)

    @api.one
    def confirm_registration(self):
        """ Email is sent only if :
        - we dont have a registration code (original logic checking setting on the event level)
        - we have a registration code and sponsoring allows sending the email.
        Otherwise juste the open status is set.
         """
        if self.registration_code:
            if self.registration_code.send_registration_mail:
                self.set_mail_set_false()
                super(EventRegistration, self).confirm_registration()
                self.is_registration_mail_sent = True
            else:
                self.state = 'open'
        else:
            self.set_mail_set_false()
            super(EventRegistration, self).confirm_registration()
            self.is_registration_mail_sent = True

    @api.one
    def set_mail_set_false(self):
        self.ensure_one()
        mail_scheduler = self.env['event.mail'].search([('event_id', '=', self.event_id.id), ('interval_type', '=', 'after_sub')], limit=1)
        mail_to_sent = mail_scheduler.mail_registration_ids.filtered(lambda m: m.registration_id.id == self.id)
        for mail in mail_to_sent:
            if mail.mail_sent:
                mail.mail_sent = False
