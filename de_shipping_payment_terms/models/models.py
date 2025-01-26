# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class deShippingTerms(models.Model):
    _name="shipping.term"
    
    name=fields.Char(string = "Shipping Terms")
    description =fields.Text(string ="Description")
    
    
    
class dePaymentTerms(models.Model):
    _name="payment.terms"
    
    name=fields.Char(string = "Payment Terms")
    description =fields.Text(string ="Description") 
