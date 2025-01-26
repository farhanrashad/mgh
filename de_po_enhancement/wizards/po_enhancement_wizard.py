from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderWizard(models.Model):
    _name = "purchase.enhancement"
    _description = "PO Wizard"

    products_po = fields.Char(string='Products')
    demand_po = fields.Float(string='Demand')
    quantity_po = fields.Float(string='Quantity Done')
    purchase_order = fields.One2many('purchase.enhancement.line', 'purchase_order_ids')
    po_line_id = fields.Many2one('purchase.order.line')
    po_line_ref = fields.Integer()
    name = fields.Char('Name', default="Detail")

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderWizard, self).create(vals)
        res.po_line_id = res.po_line_ref
        res.po_line_id.check_id = res.id
        #         raise UserError(res.po_line_id.id)
        return res


class PurchaseOrderWizardLine(models.Model):
    _name = "purchase.enhancement.line"
    _description = "PO Wizard Line"

    purchase_order_ids = fields.Many2one('purchase.enhancement')

    sale_order_po = fields.Many2one('sale.order', string='SO')
    text = fields.Text(string = "Project Description")
    quantity = fields.Float(string='Quantity')
