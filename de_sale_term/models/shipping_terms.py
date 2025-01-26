from odoo import api, fields, models
from odoo.exceptions import UserError


class ShippingTerms(models.Model):
    _name = 'shipping.terms'

    name = fields.Char(string="Shipping Terms")
    description = fields.Text(string="Description")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    shipping_id = fields.Many2one('shipping.terms', string="Please Select Your Shipping Terms")
    shipping_description = fields.Text('Description')


    payment_term_id = fields.Many2one('account.payment.term', string="Please Select Your Payment Terms")
    payment_id = fields.Many2one('payment.terms', string="Please Select Your Payment Terms")
    payment_description = fields.Text('Description')
    payment_note = fields.Text('Description')


    @api.onchange('shipping_id')
    def onchange_shipping_id(self):
        self.shipping_description = self.shipping_id.description
   
   
    @api.onchange('payment_id')
    def onchange_payment_term_id(self):
        self.payment_note= self.payment_id.description   
        
