# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def _prepare_sale_order_line(self):
        self.ensure_one()
        return {
            #'name': self.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': self.product_uom_qty,
            'standard_price': self.product_id.standard_price,
            #'taxes_id': [(6, 0, taxes_ids)],
            #'date_planned': date_planned,
            #'account_analytic_id': self.account_analytic_id.id,
            #'analytic_tag_ids': self.analytic_tag_ids.ids,
        }