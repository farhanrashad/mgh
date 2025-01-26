from odoo import api, fields, models



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    def compute_status(self):
        for rec in self:
          
            for line in rec.order_line:
                if line.qty_received < line.product_qty and line.qty_received > 0:
                    rec.status = 'partially_received'
                elif line.qty_received == 0:
                    rec.status = 'not_received'
                elif line.qty_received == line.product_qty:
                    rec.status = 'fully_received'
                else:
                    rec.status = 'not_received'
            else:
                rec.status = 'not_received'        

    status = fields.Selection([('not_received', 'Not Received'), ('partially_received', 'Partially Received'),('fully_received', 'Fully Received')], string="Received Status", compute='compute_status')
