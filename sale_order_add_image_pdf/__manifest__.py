# -*- coding: utf-8 -*-
# (c) AbAKUS IT SOLUTIONS
{
    'name': 'SO Image Product PDF',
    'version': '10.0.1.0.0',
    'author': 'AbAKUS it-solutions SARL',
    'license': 'AGPL-3',
    'summary': 'Add an image of products to SO report',
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Sale',
    'depends': ['sale', 'publisher'],
    'installable': True,
    'data': [
        'report/report_saleorder_document_image.xml',
    ]
}
