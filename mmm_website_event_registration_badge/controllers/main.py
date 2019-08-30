# -*- coding: utf-8 -*-

import base64
import werkzeug
import logging
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception
_logger = logging.getLogger(__name__)


class Binary(http.Controller):
    @http.route('/web/binary/download_document', type='http', auth="public")
    @serialize_exception
    def download_document(self, model, field, id, filename=None, **kw):
        """ Download link for files stored as binary fields.
        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        a_model = request.env[model].sudo().search([('id', '=', int(id))])
	_logger.debug("ABAKUS: id={}".format(int(id)))
	_logger.debug("ABAKUS: filename={}".format(field))
        file_content = base64.b64decode(a_model[field] or '')
        headers = werkzeug.datastructures.Headers()

        if not file_content:
            return request.not_found()
        else:
            if not filename:
                filename = '%s_%s' % (model.replace('.', '_'), id)
            headers.add('Content-Disposition', 'attachment', filename=filename)
            return request.make_response(file_content, headers)
