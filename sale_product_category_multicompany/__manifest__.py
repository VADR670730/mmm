# -*- coding: utf-8 -*-
{
    'name': "Product Category Multicompany",

    'summary': """
    Add a company field to a product categor
    """,

    'author': "Paul Ntabuye Butera, AbAKUS it-solutions",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Sale',
    'version': '10.0.1.0',
    'depends': [
        'product'
    ],
    'data': [
        'data/ir_rule.xml',

        'views/product_category_view.xml',
    ],
    'licence': '',
    'installable': True,
    'application': False,
}
