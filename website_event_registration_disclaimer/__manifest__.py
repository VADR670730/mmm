# -*- coding: utf-8 -*-
{
    'name': "Events Registration disclaimer",

    'summary': """
    """,

    'description': """
        Events Registration disclaimer

    This module adds a field in the event for the disclaimer that will be shown on the register form.

        This module has been developed by Valentin THIRION @ AbAKUS it-solutions.
    """,

    'author': "Valentin THIRION, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'website_event',
    ],

    'data': [
        'views/event_event.xml',
        'views/website_templates.xml',
    ],

    'installable': True
}
