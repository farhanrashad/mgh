from odoo import api, fields, models

class ConStockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _description = 'this is stock move model'

    expected_date = fields.Date(string='Expected Date')
    creation_date = fields.Date(string='Creation Date')
    source_document = fields.Char(string='Source Document')
    product_ids = fields.Many2one('product.product', string='Product')
    initial_demand = fields.Integer(string='Initial Demand')
    unit_of_measure = fields.Char(string='Unit Of Measure', default='Unit(s)')
    state_check = fields.Char(string='State', default='done')
    stock_move_ref = fields.Many2one('job.order', string='Ref Parent')
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure')