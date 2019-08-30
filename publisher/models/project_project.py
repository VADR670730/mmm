# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)
import tempfile
import zipfile
import base64
import urllib

class Project(models.Model):
    _inherit = 'project.project'

    production_id = fields.Many2one('publisher.production', string="Production")
    export_file = fields.Binary(attachment=True, help="This field holds the attachments export file.", readonly=True)

    def project_project_production_action(self):
        return {
            'name': _('Production'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'publisher.production',
            'type': 'ir.actions.act_window',
            'res_id': self.production_id.id
        }

    @api.model
    def create(self, values):
        if not values.get('type_ids'):
            stage_ids = self.env['publisher.project.template'].get_project_stages([('is_default_template', '=', True)])

            if stage_ids:
                values['type_ids'] = [(4, stage_id) for stage_id in stage_ids]

        return super(Project, self).create(values)

    @api.model
    def get_valid_filename(self, string):
        remove_illegals_map = dict((ord(char), None) for char in '\/*?:"<>|')
        return string.translate(remove_illegals_map)

    @api.model
    def append_attachments(self, zip_file_object, prefix = ''):
        temp_file = tempfile.mktemp(suffix='')

        existing_folders = {}

        for task in self.task_ids:

            base_folder_name = prefix + self.get_valid_filename(task.name)

            folder_name = base_folder_name
            counter = 1
            while folder_name in existing_folders:
                counter += 1
                folder_name = base_folder_name + " - " + str(counter)

            existing_folders[folder_name] = True

            for f in task.attachment_ids:
                fn = open(temp_file, 'w')
                fn.write(base64.b64decode(f.datas))
                fn.close()
                zip_file_object.write(temp_file, folder_name+"/"+f.name)

    @api.multi
    def download_attachments(self):
        self.ensure_one()

        temp_zip = tempfile.mktemp(suffix='.zip')
        zip_file_object = zipfile.ZipFile(temp_zip, "w")

        self.append_attachments(zip_file_object)

        zip_file_object.close()
        
        fn = open(temp_zip, 'r')
        self.export_file = base64.encodestring(fn.read())
        fn.close()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?' + urllib.urlencode({
                'model': 'project.project',
                'field': 'export_file',
                'id': self.id,
                'filename': self.get_valid_filename(self.name) + _(" (Attachments).zip")
            }),
            'target': 'blank',
        }