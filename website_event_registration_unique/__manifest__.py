# -*- coding: utf-8 -*-
{
    'name': "Events Registration unique",

    'summary': """
    """,

    'description': """
Events Registration unique

This models adds a boolean in the events to restrict the registration for an event for a single person at the time.

This module has been developed by Valentin THIRION @ AbAKUS it-solutions.
    """,

    'author': "Valentin THIRION, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'website_event',
        'website_event_sale',
    ],

    'data': [
        'views/event_event.xml',
        'views/website_templates.xml',
    ],

    'installable': True
}
