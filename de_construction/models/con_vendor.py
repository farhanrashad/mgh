from odoo import models, fields, api

class ConVendors(models.Model):
    _name = 'con.vendors'
    _description = 'this is contractor process model'

    name = fields.Char(string='Name')