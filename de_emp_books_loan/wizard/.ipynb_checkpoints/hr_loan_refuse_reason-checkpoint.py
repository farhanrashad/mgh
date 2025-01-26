# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrLoanRefuseWizard(models.TransientModel):
    """This wizard can be launched from an he.expense (an expense line)
    or from an hr.expense.sheet (En expense report)
    'hr_expense_refuse_model' must be passed in the context to differentiate
    the right model to use.
    """

    _name = "hr.employee.loan.refuse.wizard"
    _description = "Loan Refuse Reason Wizard"

    reason = fields.Char(string='Reason', required=True)
    hr_employee_loan_id = fields.Many2one('hr.employee.loan')

    @api.model
    def default_get(self, fields):
        res = super(HrAdvanceRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        refuse_model = self.env.context.get('hr_employee_loan_refuse_model')
        if refuse_model == 'hr.employee.loan':
            res.update({
                'hr_employee_loan_id': active_ids[0] if active_ids else False,
            })
        return res

    def loan_refuse_reason(self):
        self.ensure_one()
        if self.hr_employee_loan_id:
            self.hr_employee_loan_id.action_refuse_loan(self.reason)

        return {'type': 'ir.actions.act_window_close'}
