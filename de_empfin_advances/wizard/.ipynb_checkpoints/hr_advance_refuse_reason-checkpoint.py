# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrAdvanceRefuseWizard(models.TransientModel):
    """This wizard can be launched from an he.expense (an expense line)
    or from an hr.expense.sheet (En expense report)
    'hr_expense_refuse_model' must be passed in the context to differentiate
    the right model to use.
    """

    _name = "hr.employee.advance.refuse.wizard"
    _description = "Advance Refuse Reason Wizard"

    reason = fields.Char(string='Reason', required=True)
    hr_advance_id = fields.Many2one('hr.employee.advance')

    @api.model
    def default_get(self, fields):
        res = super(HrAdvanceRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        refuse_model = self.env.context.get('hr_advance_refuse_model')
        if refuse_model == 'hr.employee.advance':
            res.update({
                'hr_advance_id': active_ids[0] if active_ids else False,
            })
        return res

    def advance_refuse_reason(self):
        self.ensure_one()
        if self.hr_advance_id:
            self.hr_advance_id.reset_advance_request(self.reason)

        return {'type': 'ir.actions.act_window_close'}
