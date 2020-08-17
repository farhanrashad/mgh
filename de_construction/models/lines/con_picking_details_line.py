from odoo import api, fields, models


class MeterialPickingLine(models.Model):
    _name = 'meterial.picking.line'
    _description = 'Material Picking Line'


    picking_line = fields.Many2one(comodel_name="material.boq", string="", required=False, )
    # location_id = fields.Many2one('stock.location', 'Source Location', required=True)
    # location_dest_id = fields.Many2one('stock.location', 'Finished Products Location',readonly=True, required=True)
    # picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
