from odoo import api, fields, models



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    state = fields.Selection(related='order_id.state', string="State" )