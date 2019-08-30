import logging
from openerp import models, fields

_logger = logging.getLogger(__name__)

class PartnerSector(models.Model):
    _inherit = ['res.partner.sector']

    fr_external_sync_id = fields.Integer()
    nl_external_sync_id = fields.Integer()