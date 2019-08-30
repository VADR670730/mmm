# -*- coding: utf-8 -*-
{
    'name': "Sale Margin in Product",

    'summary': """
    """,

    'description': """
        Sale Margin in Product

        Adds a field 'margin' in product that will be used to auto set the value of the 'Sale Price' based on the 'Cost Price'.
        
        This module has been developed by Valentin THIRION @ AbAKUS it-solutions.
    """,

    'author': "Valentin THIRION, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': ['base', 'sale'],

    'data': [
        'views/product_template_view.xml',
    ],
}