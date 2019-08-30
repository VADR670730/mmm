import logging
from openerp import models, fields

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['res.partner']

    external_sync_id = fields.Integer()