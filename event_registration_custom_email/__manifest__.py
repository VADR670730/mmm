# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
{
    'name': "Event Registration Email Customisation",
    'summary': "Add image header, body and extra info to mail",
    'version': '10.0.1.0.0',
    'author': "AbAKUS it-solutions SARL",
    'license': 'AGPL-3',
    'depends': [
        'event',
        'event_sponsoring',
    ],
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Events',
    'data': [
        'data/email_template_data.xml',

        'views/event_views.xml',
        'views/event_registration.xml',
        'views/event_sponsoring.xml',
    ],
    'installable': True,
    'application': False,
}
