# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventRole(models.Model):
    _name = 'event.role'

    name = fields.Char('Role Name', translate=True)

    @api.model
    def name_search(self, name, args=None, operator='in', limit=100):
        args = args or []
        event_roles = self._context.get('event_roles', [False])
        event_id = self._context.get('event_id', [False])
        if 'event_roles' in self._context and event_roles and event_roles[0]:
            event_role = event_roles[0]
            recs = self.search(
                [('id', 'in', event_role[2])] + args, limit=limit)
            return recs.name_get()
        elif 'event_id' in self._context and event_id:
            event_id = self.env['event.event'].browse(
                event_id).event_role_ids.ids
            recs = self.search(
                [('id', 'in', event_id)] + args, limit=limit)
            return recs.name_get()
        return super(EventRole, self).name_search(name, args=args, operator=operator, limit=limit)
