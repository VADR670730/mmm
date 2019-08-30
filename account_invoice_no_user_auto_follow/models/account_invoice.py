# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _message_get_auto_subscribe_fields(self, updated_fields, auto_follow_fields=None):
        """ mail.thread override so user_id which has no special access allowance is not
            automatically subscribed.
        """
        if auto_follow_fields is None:
            auto_follow_fields = []
        return super(AccountInvoice, self)._message_get_auto_subscribe_fields(updated_fields, auto_follow_fields)
