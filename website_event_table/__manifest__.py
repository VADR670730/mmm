# -*- coding: utf-8 -*-
{
    'name': "Event Tables Management",
    'summary': """Add attendees table to an event
    """,
    'author': "Paul Ntabuye Butera, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'event',
    ],

    'data': [
        'views/event_table.xml',
        'views/event_event.xml',
        'views/event_registration.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True
}
