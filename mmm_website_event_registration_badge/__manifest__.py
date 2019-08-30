# -*- coding: utf-8 -*-
{
    'name': "Web Event Registration Badge L2F butterfly 1-1",

    'summary': """ Link2Fleet event badge on butterfly 1-1 paper
    """,

    'author': "Paul Ntabuye Butera, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Event',
    'version': '10.0.1.0',

    'depends': [
        'website_event',
        'website_event_table',
        'website_event_registration_info',

    ],
    'external_dependencies': {
        "python": ['PIL', 'reportlab']
    },
    'data': [
        'views/event_event.xml',
        'views/event_registration.xml',
    ],
    'css': [
        'static/src/css/link2fleet.css',
        'static/src/css/OpenSans-CondBold-webfont.css',
        'static/src/css/OpenSans-CondLightItalic-webfont.css',
        'static/src/css/OpenSans-CondLight-webfont.css',
    ],
    'installable': True
}
