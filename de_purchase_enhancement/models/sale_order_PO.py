from odoo import fields, models, _


class sale_order_PO(models.Model):
    _inherit = 'sale.order'

    po_count=fields.Integer(compute='compute_count')

    def get_PurchaseOrder(self):
        """
        To get Count against SO for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'domain': [('auto_complete_id', '=', self.id)],
            'target': 'current',
            'view_mode': 'list,form',
        }

    def compute_count(self):
        for record in self:
            record.po_count = self.env['purchase.order'].search_count(
                [('auto_complete_id', '=', self.id)])