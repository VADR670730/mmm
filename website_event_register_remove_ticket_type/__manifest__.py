# -*- coding: utf-8 -*-
{
    'name': "Events Registration Form Remove 'ticket-type'",

    'summary': """
    """,

    'description': """
        Events Registration Form Remove 'ticket-type'

        This module removes the text 'ticket-type' and info on the registration form for an event.

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
        'views/website_templates.xml',
    ],

    'installable': True
}
