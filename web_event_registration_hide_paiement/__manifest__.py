# -*- coding: utf-8 -*-
{
    'name': "Event Hide Paiement",

    'summary': """
        Event Hide Paiement in Website
    """,

    'description': """
        Event Hide Paiement in Website

    This module will bypass the paiement process when user want to register to en event.

    """,

    'author': "ABAKUS IT-SOLUTIONS",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Website',
    'version': '10.0.1.0.0',

    'depends': [
        'website_event_sale',
    ],

    'data': [
        'views/wizard_checkout_template.xml',
        'views/checkout_template.xml',
        'views/confirmation_template.xml',
    ],

    'installable': True
}
