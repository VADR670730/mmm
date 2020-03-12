# -*- coding: utf-8 -*-
{
    'name': "Remove draft offers after 24 hours",
    'summary': """
        Remove draft offers after 24 hours""",

    'description': """
        This module will remove all draft sale order lines if the user did not confirmed the registration.
    """,
    'author': "ABAKUS IT-SOLUTIONS",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Sale',
    'version': '10.0.1.0',
    'depends': [
        'sale',
    ],
    'data': [
        "data/cron.xml",
    ],

    'application': True,
}
