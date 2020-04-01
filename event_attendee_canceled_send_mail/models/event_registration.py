# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    user_to_send_id = fields.Many2one("res.users")

    @api.model
    def write(self, vals):
        if self.state == 'open' and vals.get("state",None) == 'cancel':
            self.send_attendee_canceled_email()
        registration = super(EventRegistration, self).write(vals)
        return registration

    def send_attendee_canceled_email(self):
        users = self.env["res.users"].search([('send_canceled_registration', '=', 'True')])
        template_id = self.env.ref('event_attendee_canceled_send_mail.notify_attendee_canceled_template')
        for user in users:
            self.user_to_send_id = user.id
            if template_id:
                template_id.sudo().send_mail(self.id, force_send=True)
