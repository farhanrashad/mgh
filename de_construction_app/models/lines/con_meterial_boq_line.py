from odoo import api, fields, models


class MeterialBoqLine(models.Model):
    _name = 'meterial.boq.line'


    req_line = fields.Many2one(comodel_name="meterial.boq", string="", required=False, )
    # product_id = fields.Many2one("product.product", string="Product")
    name = fields.Char(string="Description", required=False, )
    product_uom_qty = fields.Float(string='Quantity',)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    vendor_id = fields.Many2one(comodel_name="con.vendors", string="Vendors", required=False, )