from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPickingWizard(models.Model):
    _name = "stock.enhancement"
    _description = "Stock Picking Wizard"

    products_sp = fields.Many2one('product.product', 'Products')
    demand_sp = fields.Float(string='Demand')
    quantity_sp = fields.Float(string='Quantity Done')
    stock_pick = fields.One2many('stock.enhancement.line', 'stock_order_ids')
    ps_line_id = fields.Many2one('stock.move')
    ps_line_ref = fields.Integer()
    name = fields.Char('Name', default="Detail SO")

    @api.model
    def create(self, vals):
        res = super(StockPickingWizard, self).create(vals)
        res.ps_line_id = res.ps_line_ref
        res.ps_line_id.check_id_stock = res.id
        res.products_sp = res.ps_line_id.product_id.id
        for line in res.stock_pick:
            delivery = self.env['stock.picking'].search([('origin', '=', line.sale_order_sp.name)])
            for dell in delivery.move_ids_without_package:
                if dell.product_id.id == res.products_sp.id:
                    dell.quantity_done = line.quantity
        return res


class StockPickingWizardLine(models.Model):
    _name = "stock.enhancement.line"
    _description = "Stock Picking Wizard Line"

    stock_order_ids = fields.Many2one('stock.enhancement')

    sale_order_sp = fields.Many2one('sale.order', string='SO')
    text = fields.Text(string = "Project Description")
    quantity = fields.Float(string='Quantity')

