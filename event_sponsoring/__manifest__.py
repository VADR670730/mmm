# -*- coding: utf-8 -*-
# (c) AbAKUS IT Solutions
{
    'name': "Event sponsoring",
    'summary': "Event sponsporing managment",
    'version': '10.0.1.1',
    'license': 'AGPL-3',
    'author': "AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'depends': [
        'event',
        'website_event_registration_info',
        'website_event_sub_events',
        'website_event_table',
    ],
    'category': 'Sale',
    'data': [
        'security/ir.model.access.csv',

        'views/partner.xml',
        'views/event_views.xml',

        'views/event_registration.xml',
        'views/event_registration_code_view.xml',
        'views/event_views.xml',
        'views/sale_order_line.xml',

        'views/website_portal_sale_templates.xml',
        'views/website_event_templates.xml',
    ],
}