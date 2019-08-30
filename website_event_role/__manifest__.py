# -*- coding: utf-8 -*-
# Part of AktivSoftware See LICENSE file for full
# copyright and licensing details.
{
    'name': "Website Event Role",

    'summary': """
        Website Event Role""",

    'description': """
        Website Event Role :
        - Role in Event model
        - Roles in Event Registration
        - Website Event Registration
    """,

    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'category': 'event',
    'version': '10.0.1.0.0',
    'depends': ['event', 'website_event_registration_info'],
    'data': [
        'security/role_security.xml',
        'security/ir.model.access.csv',
        'views/event_config_settings.xml',
        'views/event_role.xml',
        'views/event_event.xml',
        'views/event_registration.xml',
        'views/website_templates.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False
}
