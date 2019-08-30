# -*- coding: utf-8 -*-
{
    'name': "Events Registration with new fields",

    'summary': """
    """,

    'description': """
        Events Registration with new fields

    This module adds some fields on the registration model and on the form online:
    - Function
    - Firstname
    - Lastname
    - Company
    - Language

    On the registration (in the backend), it also adds:
    - URL for the event poll
    - Code for the event poll

        This module has been developed by Valentin THIRION @ AbAKUS it-solutions.
    """,

    'author': "Valentin THIRION, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'website_event_sale',
    ],

    'data': [
        'views/event_registration.xml',
        'views/website_templates.xml',
    ],

    'installable': True
}
