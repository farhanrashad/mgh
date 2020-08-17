from odoo import api, fields, models


class ConStockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _description = 'Stock Move Line Extension'

    expected_date = fields.Date(string='Expected Date')
    creation_date = fields.Date(string='Creation Date')
    source_document = fields.Char(string='Source Document')
    product_ids = fields.Many2one(comodel_name='product.product', string='Product Id')
    initial_demand = fields.Float(string='Initial Demand')
    unit_of_measure = fields.Many2one(comodel_name='uom.uom', string='Unit Of Measure')
    state_check = fields.Char(string='State', default='done')
    stock_move_ref = fields.Many2one(comodel_name='job.order', string='Ref Parent')
