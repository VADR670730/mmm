# -*- coding: utf-8 -*-
{
    'name': "Sale Workflow Rights",

    'summary': """
    """,

    'description': """
        Sale Workflow Rights
        
        Adds "Option" state to the workflow.
        Restricts rights for salesmen depending on the state (Authorized to write only if state is Draft or Option).
        
        This module has been developed by Jason PINDAT, intern @ AbAKUS it-solutions.
    """,

    'author': "Jason PINDAT, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'sale'
    ],

    'data': [
        'views/sale_order.xml'
    ],
}
