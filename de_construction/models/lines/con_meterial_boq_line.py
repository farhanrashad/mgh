from odoo import api, fields, models


class MaterialBoqLine(models.Model):
    _name = 'material.boq.line'
    _description = 'Material BOQ Line'

    req_line = fields.Many2one(comodel_name='material.boq', string='')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    description = fields.Char(string='Description', required=True)
    product_uom_qty = fields.Float(string='Initial Demand')
    product_uom = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure')
    reserved_qty = fields.Float(string='Reserved')
    done_qty = fields.Float(string='Done')
    requisition_action = fields.Selection(
        [('purchase_order', 'Purchase Order'),
         ('internal_picking', 'Internal Picking')],
        string='Requisition Action')
    vendor_id = fields.Many2many(comodel_name='res.partner', string='Vendors')
