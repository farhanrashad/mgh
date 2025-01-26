# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line' 

    ora_account_code = fields.Char(string='Account Code')            
    
    