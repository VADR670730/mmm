# -*- coding: utf-8 -*-
{
    'name': "Send mail when attendee cancelled",
    'summary': "Send mail when attendee cancelled",
    'description' : "This module will send an email if an attendee cancel his registration",
    'version': '10.0.1.1',
    'license': 'AGPL-3',
    'author': "ABAKUS IT-SOLUTIONS",
    'website': "http://www.abakusitsolutions.eu",
    'depends': [
        'event',
    ],
    'category': 'Event',
    'data': [
        'views/res_users.xml',

        'report/mail_templates.xml',
    ],
}