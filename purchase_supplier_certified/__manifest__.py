# -*- coding: utf-8 -*-
{
    'name': "Certified Supplier",

    'summary': """
    """,

    'description': """
        Certified Supplier

        Adds a boolean 'certified' on the supplier form and allows to search on them.

        This module has been developed by Valentin THIRION @ AbAKUS it-solutions.
    """,

    'author': "Valentin THIRION, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Purchase',
    'version': '10.0.1.0',

    'depends': [
        'base',
        'purchase'
    ],

    'data': [
        'views/res_partner_view.xml'
    ],
}