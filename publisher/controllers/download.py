from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception
import base64
import werkzeug

class Binary(http.Controller):
    @http.route('/web/binary/download_document', type='http', auth="public")
    @serialize_exception
    def download_document(self,model,field,id,filename=None, **kw):
        """ Download link for files stored as binary fields.
        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        Model = request.env[model].sudo().search([('id', '=', int(id))])
        filecontent = base64.b64decode(Model[field] or '')
        headers = werkzeug.datastructures.Headers()

        if not filecontent:
            return request.not_found()
        else:
            if not filename:
                filename = '%s_%s' % (model.replace('.', '_'), id)

            headers.add('Content-Disposition', 'attachment', filename=filename)
            return request.make_response(filecontent,headers)