# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

class RedCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
        
    def write(self, val):
        
        a = self.id
        rec = self.env['res.currency.rate'].search([('id','=',a)]).name
        today = date.today()
        if rec != today:
            raise UserError(('Sorry you can not make any changes here now'))
        return super(RedCurrencyRate, self).write(val)


    def unlink(self):
        raise UserError(('Sorry you can not delete .'))

     
