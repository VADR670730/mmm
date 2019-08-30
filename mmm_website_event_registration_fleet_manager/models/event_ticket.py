# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class EventTicketFleetManager(models.Model):
    _inherit = 'event.event.ticket'

    ask_for_is_fleet_manager = fields.Boolean()
    ask_for_is_participating_blue_run = fields.Boolean()
