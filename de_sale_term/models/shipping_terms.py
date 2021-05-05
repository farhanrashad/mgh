from odoo import api, fields, models
from odoo.exceptions import UserError


class ShippingTerms(models.Model):
    _name = 'shipping.terms'

    name = fields.Char(string="Shipping / Payment Terms")
    description = fields.Text(string="Description")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    shipping_id = fields.Many2one('shipping.terms', string="Please Select Your Shipping / Payment Terms")
    shipping_description = fields.Text('Description')

    @api.onchange('shipping_id')
    def onchange_shipping_id(self):
        self.shipping_description = self.shipping_id.description
