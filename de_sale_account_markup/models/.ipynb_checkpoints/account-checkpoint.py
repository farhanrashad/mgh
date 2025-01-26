from odoo import api, fields, models, _
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError

import math
import logging

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    markup = fields.Float(string="Markup (%)")
    price_excl_markup = fields.Float(string="Price Excl Markup",)
    
    