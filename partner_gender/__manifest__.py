# -*- coding: utf-8 -*-
{
    'name': "Partner Gender",

    'summary': """
    """,

    'description': """
        Partner Gender
        
        Adds the gender field to a physical partner
        
        This module has been developed by Jason PINDAT, intern @ AbAKUS it-solutions.
    """,

    'author': "Jason PINDAT, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Base',
    'version': '10.0.1.0',

    'depends': ['base'],

    'data': [
        'views/res_partner.xml',

        'security/ir.model.access.csv',

        'data/res_partner_genders.xml',
    ],
}