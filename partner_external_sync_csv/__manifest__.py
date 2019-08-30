# -*- encoding: utf-8 -*-
{
    'name': "Partner Sync FTP/CSV",

    'summary': """Partner contact sync via FTP from CSV files
    """,
    'author': "Valentin Thiirion @ AbAKUS it-solutions",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'partner-contact',
    'version': '1.0',
    'depends': [
        'contacts',
        'partner_sector',
        'partner_social_networks',
        'partner_firstname_surname',
    ],
    'sequence': 1,
    'data': [
        'views/res_partner_view.xml',
        'views/res_partner_sector_view.xml',
        'views/res_partner_sync_views.xml',
        'data/contact_sync_cron.xml',
    ],
    'demo': [
    ],
}