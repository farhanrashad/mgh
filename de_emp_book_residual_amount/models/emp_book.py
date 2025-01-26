from odoo import models, fields, api


class TotalOrderLineQty(models.Model):
    _inherit = 'hr.expense.prepayment'

    residual_amount = fields.Monetary(string='Residual Amount', compute='_calculate_amount_residual', store=True,
                                      help="Amount Residual")

    def _calculate_amount_residual(self):
        for rs in self:
            tot_residual_amount = 0
            for line in rs.expense_prepayment_line_ids:
                tot_residual_amount += line.amount_residual
            rs.residual_amount = tot_residual_amount
