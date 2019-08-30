# -*- coding: utf-8 -*-


def post_init_hook(cr, registry):
    """ Add CZC format to address format """
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(city)s %(state_code)s %(zip)s\n%(country_name)s',
        E'%(country_zip_city)s'
        )
    """
    cr.execute(query)


def uninstall_hook(cr, registry):
    """ Remove CZC from address a bring back default format format """
    # Remove %(country_zip_city)s\n from address_format
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(country_zip_city)s\n',
        E'%(city)s %(state_code)s %(zip)s\n%(country_name)s\n'
        )
    """
    cr.execute(query)

    # Remove %(country_zip_city)s from address_format
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(country_zip_city)s',
        E'%(city)s %(state_code)s %(zip)s\n%(country_name)s\n'
        )
    """
    cr.execute(query)
