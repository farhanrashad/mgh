from odoo import api, fields, models


class MaterialPlanningLine(models.Model):
    _name = 'material.planning.line'
    _description = 'Material Planning Line'
    _rec_name = 'product_id'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    name = fields.Text(string='Description', related='product_id.description')
    product_uom_quantity = fields.Float(string='Quantity')
    product_uom = fields.Many2one(comodel_name='uom.uom', string='Unit Of Measure')
    job_order_ref = fields.Many2one(comodel_name='job.order', string='ref parent')

