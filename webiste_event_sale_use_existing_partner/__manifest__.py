# -*- coding: utf-8 -*-
{
    'name': "Use existing partner on sale orders",
    'description':"This module will use existing partners if they exists when an user register for an event",
    'author': "ABAKUS IT-SOLUTIONS",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Sale',
    'version': '10.0.1.0',
    'depends': [
        'sale',
        'website_sale',
        'website_event_country_default',
    ],
    'data': [
        "views/templates.xml",
    ],

    'application': True,
}