# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)


class Event(models.Model):
    """ We add additional custom field to be featured in custom mail """
    _inherit = "event.event"

    mail_header_logo = fields.Binary(string='Email custom header logo (200 x 600)')
    mail_custom_text = fields.Text(srint='Custom event text', translate=True)


class EventType(models.Model):
    _inherit = "event.type"

    @api.model
    def _default_event_mail_ids(self):
        """ We override this so that email uses our custom template instead of the original one"""
        _logger.debug("ABAKUS: Using Custom mail template for NOW")
        return [(0, 0, {
            'interval_unit': 'now',
            'interval_type': 'after_sub',
            'template_id': self.env.ref('event_registration_custom_email.event_subscription_custom')
        }), (0, 0, {
            'interval_nbr': 2,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('event.event_reminder')
        }), (0, 0, {
            'interval_nbr': 15,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('event.event_reminder')
        })]

    event_mail_ids = fields.One2many('event.mail', 'event_id',
                                     string='Mail Schedule',
                                     default=lambda self: self._default_event_mail_ids(),
                                     copy=False)
