# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
{
    'name': "Event Registration Portal Update via Token",
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
        'views/event_event.xml',
        'views/event_registration.xml',
        'views/event_registration_code_view.xml',
        'views/website_portal_sale_template.xml',
    ],
    'installable': True,
    'application': False,
}
