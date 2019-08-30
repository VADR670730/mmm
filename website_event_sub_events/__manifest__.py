# -*- coding: utf-8 -*-

{
    'name': "Website Event Sub Events",

    'summary': """
        Updated the form view for Event registration,Event details.""",

    'description': """
        Added new models, updated form view for event registration, attendee
        registration, smart button and also updated website registartion
        form view.
    """,

    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'category': 'Event',
    'version': '10.0.1.0.0',
    'depends': [
        'website_event_role', 'website_event',
        'website_event_sale_multicompany'],
    'data': [
        'security/ir.model.access.csv',

        'views/event_sub_event_line_views.xml',
        'views/event_event_view.xml',
        'views/event_registration_view.xml',
        'views/website_event_template.xml',
    ],
}
