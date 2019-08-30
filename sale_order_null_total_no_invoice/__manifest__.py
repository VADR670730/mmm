# -*- coding: utf-8 -*-
{
    'name': "Sale Order No Total No Invoice",

    'summary': """
    """,

    'description': """
Sale Order No Total No Invoice

When the sale order is changed from "send draft" to "sale", the modules checks if sum of order lines is equal to 0 and defines the state of invoice to "no" in that case.

This module has been developed by François WYAIME @ AbAKUS it-solutions.
    """,

    'author': "François WYAIME, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'sale',
    ],

    'data': [
    ],

    'installable': True
}
