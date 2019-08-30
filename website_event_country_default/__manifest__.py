# -*- coding: utf-8 -*-
{
    'name': "Event Default Country in Website",

    'summary': """
        Event default country in Website
    """,

    'description': """
        Event default country in Website

    This module will set the default country in the address form of website from Event.

    """,

    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",

    'category': 'Website',
    'version': '10.0.1.0.0',

    'depends': [
        'website_event_sale',
    ],

    'data': [
        'views/website_sale_templates.xml',
    ],

    'installable': True
}
