from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderEnhancement(models.Model):
    _inherit = 'purchase.order'

    subject = fields.Char(string="Subject")


class PurchaseOrderEnhancementLine(models.Model):
    _inherit = 'purchase.order.line'

    check = fields.Char(string="Check")
    check_id = fields.Many2one('purchase.enhancement')

    def view_save_data(self):
        return {
            'name': 'PO',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'list,form',
            'domain': [('id', '=', self.check_id.id)],
            'res_model': 'purchase.enhancement',
            'target': 'current'
        }


class SrockMoveLineInherit(models.Model):
    _inherit = 'stock.move'

    name = fields.Char('Name')
    check_id_stock = fields.Many2one('stock.enhancement')

    def view_stock_data(self):
        return {
            'name': 'SP',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'list,form',
            'domain': [('id', '=', self.check_id_stock.id)],
            'res_model': 'stock.enhancement',
            'target': 'current'
        }