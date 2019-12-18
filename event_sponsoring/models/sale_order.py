# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     @api.multi
#     def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
#         """ Override the one from website_event_sale in order to apply discount if registration_code available """
#         values = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
#         _logger.debug("ABAKUS: updating the cart with valuees: {}".format(values))
#         if 'attendee_ids' in values:
#             Registration = self.env['event.registration'].sudo()
#             for attendee_id in values['attendee_ids']:
#                 registration = Registration.browse(attendee_id)
#                 if registration.registration_code:
#                     _logger.debug("ABAKUS: found an attendee with a reg code: {}".format(
#                         registration.registration_code.code))
#                     if line_id:
#                         line_id.write({
#                             'discount': registration.registration_code.discount_rate,
#                             'registration_code_info': "{} ,*({})".format(
#                                 registration.registration_code.code,
#                                 registration.registration_code.discount_rate),
#                         })
#                     else:
#                         values['discount'] = registration.registration_code.discount_rate
#                         values['registration_code_info'] = "{} ,**({})".format(
#                             registration.registration_code.code,
#                             registration.registration_code.discount_rate)
#                     break
#         return values


class SaleOrderLine(models.Model):
    """ A SOL has an event_ticket_id that auto creates a linked registration.
        Our registration code is reference on said registration(s).
     """
    _inherit = 'sale.order.line'

    registration_code_id = fields.Many2one('event.registration.code', string="Code")

    @api.multi
    def _update_registrations(self, confirm=True, registration_data=None):
        """ We override the method in order to extract registration codes and apply them"""
        super(SaleOrderLine, self)._update_registrations(confirm, registration_data)
        Registration = self.env['event.registration'].sudo()
        registrations = Registration.search([('sale_order_line_id', 'in', self.ids), ('state', '!=', 'cancel')])
        _logger.debug("ABAKUS: found {} registrations".format(len(registrations)))
        for so_line in self.filtered('event_id'):
            existing_registrations = registrations.filtered(lambda self: self.sale_order_line_id.id == so_line.id)
            _logger.debug("ABAKUS: found {} existing_registrations".format(len(existing_registrations)))
            for registration in existing_registrations:
                _logger.debug("ABAKUS: processing registration: {}".format(registrations))
                if registration.registration_code:
                    # apply it !
                    if registration.registration_code.available_quota > 0:
                        self.registration_code_id = registration.registration_code
                        # NOTE: VT needs to sort out the co-existence of discount (computed) and discount_base(new)
                        # NOTE: this alteration is inherited from vertical_publisher module
                        # NOTE: Provided there is no agency commission on selling events it is safe to
                        # NOTE: update discount_base instead of
                        # NOTE: self.discount = registration.registration_code.discount_rate
                        self.discount_base = registration.registration_code.discount_rate
                        self.discount = registration.registration_code.discount_rate
                        self._compute_tax_id()
                        # we can break at this point since we have 1 attendee per SOL
                    break
        return True

    # def create(self, vals):
    #     _logger.debug("ABAKUS: creating SOL with vals={}".format(vals))
    #     sol = super(SaleOrderLine, self).create(vals)
    #     return sol

    @api.multi
    def _prepare_invoice_line(self, qty):
        """ Override this to add registration code info from SOL to invoice (if any)"""
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.registration_code_id:
            res.update({'name': res['name'] + ' - ' + self.registration_code_id.name})
        return res
