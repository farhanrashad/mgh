from odoo import api, fields, models, _
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError

import math
import logging

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    markup = fields.Float(string="Markup (%)")
    price_excl_markup = fields.Float(string="Price Excl Markup",)
    
    @api.onchange('price_excl_markup')
    def _onchange_price_excl_markup(self):
        self.price_unit = self.price_excl_markup + (self.price_excl_markup * self.markup) / 100
        
    @api.onchange('markup')
    def _onchange_markup(self):
        self.price_unit = self.price_excl_markup + (self.price_excl_markup * self.markup) / 100