# -*- coding: utf-8 -*-
{
    'name': "Events Registration with Fleet Manager and sub events",

    'summary': """
    """,

    'description': """

Events Registration with Fleet Manager and Blue Run

This module adds some fields on the registration model and on the form online:
- is Fleet Manager
- Participates to the 'Blue-Run' (only if 'is Fleet Manager')

It also adds a 'sub-event' management that can be added to an event and selected by the registered people on the register page.

        This module has been developed by Valentin THIRION @ AbAKUS it-solutions.
    """,

    'author': "Valentin THIRION, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'website_event_registration_info',
    ],

    'data': [
        'views/event_registration.xml',
        'views/event_event.xml',
        'views/website_templates.xml',
        'views/event_sub_event.xml',

        'security/ir.model.access.csv',
    ],

    'installable': True
}
