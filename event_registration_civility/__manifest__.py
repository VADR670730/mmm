# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
{
    'name': "Event Registration Civility",
    'version': '10.0.1.0.0',
    'author': "AbAKUS it-solutions SARL",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'event',
        'website_event_registration_info',
    ],
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Events',
    'data': [
        'views/event_registration.xml',
        'views/website_templates.xml',
    ],
    'installable': True,
    'application': False,
}
