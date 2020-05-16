from odoo import api, fields, models

class MaterialPlanningLine(models.Model):
    _name = 'material.planning.line'
    _description = 'this is material planning model'

    # product_id = fields.Char(string="Product", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    name = fields.Char(string='Description')
    product_uom_quantity = fields.Integer(string='Quantity')
    product_uom = fields.Char(string='Unit Of Measure', default='Unit(s)')
    job_order_ref = fields.Many2one('job.order', string='ref parent')

