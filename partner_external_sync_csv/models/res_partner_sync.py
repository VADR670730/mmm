from odoo import models, fields, api, exceptions, _
import odoo.tools as tools
from ftplib import FTP
import logging, os
import StringIO
import datetime

_logger = logging.getLogger(__name__)

class PartnerSync(models.Model):
    _name = 'res_partner_sync'

    name = fields.Char()
    active = fields.Boolean()
    ftp_url = fields.Char()
    ftp_user = fields.Char()
    ftp_pass = fields.Char()
    ftp_port = fields.Integer()
    ftp_folder = fields.Char()
    companies_file_prefix = fields.Char()
    contacts_file_prefix = fields.Char()
    sectors_file_prefix = fields.Char()
    date_last_sync = fields.Date()
    passed_test = fields.Boolean()
    is_test_mode = fields.Boolean()
    test_mode_limit = fields.Integer()
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('res_partner_sync.res_partner_sync'))

    # FTP SYSTEM METHODS
    @api.multi
    def connect(self):
        ftp = FTP(self.ftp_url, self.ftp_user, self.ftp_pass)
        ftp.cwd(self.ftp_folder)
        return ftp

    @api.multi
    def close(self, ftp):
        ftp.close()

    # retrun the filename in a list
    @api.multi
    def list_file(self, ftp):
        return ftp.nlst()

    @api.multi
    def read_file(self, ftp, filename):
        data = StringIO.StringIO()
        ftp.retrbinary("RETR " + filename, data.write)
        return data.getvalue()

    # Odoo data methods ------------------------------

    # This method creates the partner (company) in the DB if it doesn't exists, and update it if the external id is known
    @api.model
    def addCompany(self, external_id, name, vat, street, street_number, zip, city, phone, email, website, linkedin, twitter, sector):
        # Get sector
        main_sector_id = False
        secondary_sector_ids = []
        if sector != "":
            if ',' in sector:
                sectors = sector.split(',')
                main_sector_id = self.env['res.partner.sector'].search([['nl_external_sync_id', '=', int(sectors[0])]]).id
                for sector in sectors[1:]:
                    second_sector_id = self.env['res.partner.sector'].search([['nl_external_sync_id', '=', sector]]).id
                    if second_sector_id != False and second_sector_id != main_sector_id:
                        secondary_sector_ids.append(second_sector_id)
            else:
                main_sector_id = self.env['res.partner.sector'].search([['nl_external_sync_id', '=', int(sector)]]).id

        # Check if exists
        partner_id = self.env['res.partner'].search([['external_sync_id', '=', int(external_id)]])
        if len(partner_id) > 0:
            partner_id.write({
                'company_type': 'company',
                'name': name,
                'street': str(street + " " + street_number),
                'zip': zip, 
                'city': city,
                'phone': phone,
                'email': email,
                'website': website,
                'linkedin_link': linkedin,
                'twitter_link': twitter,
                'sector_id': main_sector_id,
                'company_id': self.company_id.id,
                'secondary_sector_ids': [(6, 0,[y for y in secondary_sector_ids])],
            })
        else:
            partner_id = self.env['res.partner'].create({
                'company_type': 'company',
                'name': name,
                'street': str(street + " " + street_number),
                'zip': zip, 
                'city': city,
                'phone': phone,
                'email': email,
                'website': website,
                'linkedin_link': linkedin,
                'twitter_link': twitter,
                'sector_id': main_sector_id,
                'external_sync_id': int(external_id),
                'company_id': self.company_id.id,
                'secondary_sector_ids': [(6, 0,[y for y in secondary_sector_ids])],
            })

        # VAT
        vat = vat.replace(" ", "").replace(".", "")
        if len(vat) > 0 and len(vat) < 12:
            prefix = vat[:2]
            suffix = vat[2:]
            suffix = str("0" + suffix)
            vat = prefix + suffix
        try:
            partner_id.write({
                'vat': vat,
            })
        except exceptions.ValidationError, e:
             partner_id.write({
                'vat': "",
                'comment': str("\nERROR: " + str(e)) if (partner_id.comment == False) else str(partner_id.comment + "\nERROR: " + str(e)),
            })

    # This method creates the partner (contact) in the DB if it doesn't exists, and update it if the external id is known
    @api.model
    def addContact(self, external_id, company_external_id, firstname, lastname, email, phone, linkedin, facebook, twitter):
        # Get company
        company_id = False
        if company_external_id != "":
            company_id = self.env['res.partner'].search([['external_sync_id', '=', int(company_external_id)]]).id
    
        # Check if exists
        partner_id = self.env['res.partner'].search([['external_sync_id', '=', int(external_id)]])
        if len(partner_id) > 0:
            partner_id.write({
                'company_type': 'person',
                'parent_id': company_id,
                'firstname': firstname,
                'surname': lastname,
                'name': str(firstname + " " + lastname),
                'phone': phone,
                'email': email,
                'linkedin_link': linkedin,
                'twitter_link': twitter,
                'facebook_link': facebook,
                'company_id': self.company_id.id,
            })
        else:
            sector_id = self.env['res.partner'].create({
                'company_type': 'person',
                'parent_id': company_id,
                'firstname': firstname,
                'surname': lastname,
                'name': str(firstname + " " + lastname),
                'phone': phone,
                'email': email,
                'linkedin_link': linkedin,
                'twitter_link': twitter,
                'facebook_link': facebook,
                'external_sync_id': int(external_id),
                'company_id': self.company_id.id,
            })

    # This method creates the sector in the DB if it doesn't exists, and update it if the external id is known
    @api.model
    def addSector(self, nl_external_id, name_nl, fr_external_id, name_fr):
        # Bool for translation existence
        translated = False
        # Check if exists
        sector_id = self.env['res.partner.sector'].search([['nl_external_sync_id', '=', int(nl_external_id)]])
        if len(sector_id) > 0:
            sector_id.fr_external_sync_id = fr_external_id

        else:
            sector_id = self.env['res.partner.sector'].create({
                'name': name_nl,
                'nl_external_sync_id': int(nl_external_id),
                'fr_external_sync_id': int(fr_external_id),
            })

        self.add_translation('nl_BE', sector_id.id, 'res.partner.sector,name', name_nl, name_nl)
        self.add_translation('fr_BE', sector_id.id, 'res.partner.sector,name', name_nl, name_fr)

    # This method creates the translation for the given parameters if it doesn't exist
    def add_translation(self, lang, res_id, res_model, source, value):
        translation_id = self.env['ir.translation'].search([['res_id', '=', res_id], ['name', '=', res_model], ['lang', '=', lang], ['source', '=', source]])
        if len(translation_id) > 0:
            if len(translation_id) > 1:
                translation_id = translation_id[0]
            translation_id.value = value
        else:
            self.env['ir.translation'].create({
                'lang': lang,
                'res_id': res_id,
                'type': 'model',
                'name': res_model,
                'source': source,
                'state': 'translated',
                'value': value,
            })
            
    # -----------------------------------------------------------------------
    # METHOD ACTIONS TRIGERED BY BUTTONS
    @api.multi
    def action_test_ftp_server(self):
        self.passed_test = False
        try:
            ftp = self.connect()
        except Exception, e:
            raise exceptions.ValidationError(_("Connection Test Failed!, Here is what we got instead:\n %s") % e)
        finally:
            try:
                if ftp:
                    self.close(ftp)
            except Exception:
                pass
        self.passed_test = True

    @api.one
    def action_sync(self):
        for setting in self:
            if setting.passed_test:
                # Connect
                ftp = setting.connect()

                # Get files
                file_names = setting.list_file(ftp)

                for my_file in file_names:
                    file_content = setting.read_file(ftp, my_file).replace('"', '').replace('&amp;', '&').split("\n")

                    # Parse companies files
                    if setting.companies_file_prefix in my_file:
                    
                        # Counter for test mode
                        counter = 0
                    
                        allowedHeaderNames = ['odoo', 'id company', 'name company', 'vat nr company', 'street name company', 'street nr company', 'zip company', 'city company', 'phone company', 'e-mail company', 'website company', 'linked-in company', 'twitter company', 'sector (categorie) company']

                        # Check first line :
                        if file_content[0].split(";") != allowedHeaderNames:
                            raise exceptions.ValidationError(_("Error! The structure of the CSV file (%s) is not correct") % my_file)

                        for line in file_content[1:len(file_content)]:
                            dataLine = line.split(";")
                            if len(dataLine) < len(allowedHeaderNames):
                                continue
                            self.addCompany(dataLine[1], dataLine[2], dataLine[3], dataLine[4], dataLine[5], dataLine[6], dataLine[7], dataLine[8], dataLine[9], dataLine[10], dataLine[11], dataLine[12], dataLine[13])

                            # Test mode check
                            counter = counter + 1
                            if setting.is_test_mode and counter == setting.test_mode_limit:
                                break

                        continue

                    # Parse contacts files
                    if setting.contacts_file_prefix in my_file:

                        # Counter for test mode
                        counter = 0

                        allowedHeaderNames = ['odoo', 'company', 'ID', 'order', 'last_name', 'first_name', 'email', 'phone_number', 'linkedin', 'facebook', 'twitter']

                        # Check first line :
                        if file_content[0].split(";") != allowedHeaderNames:
                            raise exceptions.ValidationError(_("Error! The structure of the CSV file (%s) is not correct") % my_file)

                        for line in file_content[1:len(file_content)]:
                            dataLine = line.split(";")
                            if len(dataLine) < len(allowedHeaderNames):
                                continue
                            self.addContact(dataLine[2], dataLine[1], dataLine[5], dataLine[4], dataLine[6], dataLine[7], dataLine[8], dataLine[9], dataLine[10])

                            # Test mode check
                            counter = counter + 1
                            if setting.is_test_mode and counter == setting.test_mode_limit:
                                break

                        continue

                    # Parse sector files
                    if setting.sectors_file_prefix in my_file:
                        # Counter for test mode
                        counter = 0
                        
                        allowedHeaderNames = ['ID', 'Name NL', 'ID FR', 'Name FR']

                        # Check first line :
                        if file_content[0].split(";") != allowedHeaderNames:
                            raise exceptions.ValidationError(_("Error! The structure of the CSV file (%s) is not correct") % my_file)

                        for line in file_content[1:len(file_content)]:
                            dataLine = line.split(";")
                            if len(dataLine) < len(allowedHeaderNames):
                                continue
                            self.addSector(dataLine[0], dataLine[1], dataLine[2], dataLine[3])

                            # Test mode check
                            counter = counter + 1
                            if setting.is_test_mode and counter == setting.test_mode_limit:
                                break
                        
                        continue

                setting.date_last_sync = datetime.datetime.now()
                    
                # Close
                ftp.close()

    def _cron_sync_contacts(self):
        setting_ids = self.env['res_partner_sync'].search([['active', '=', True]])
        for setting in setting_ids:
            setting.action_sync()
    