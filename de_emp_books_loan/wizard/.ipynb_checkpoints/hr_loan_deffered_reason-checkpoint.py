# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrAdvanceDefferedWizard(models.TransientModel):
    """This wizard can be launched from an he.employee.advances
    'hr_employee_advance_model' must be passed in the context to differentiate
    the right model to use.
    """

    _name = "hr.employee.advance.deffered.wizard"
    _description = "Employee Advance Deffered Wizard"

    reason = fields.Char(string='Reason', required=True)
    deffered_period = fields.Integer(string='Deffered Period')
    hr_advance_id = fields.Many2one('hr.employee.advance')

    @api.model
    def default_get(self, fields):
        res = super(HrAdvanceDefferedWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        advance_deffered_model = self.env.context.get('hr_advance_deffered_model')
        if advance_deffered_model == 'hr.employee.advance':
            res.update({
                'hr_advance_id': active_ids[0] if active_ids else False,
            })
        return res

    def advance_deffered_reason(self):
        self.ensure_one()
        if self.hr_advance_id:
            self.hr_advance_id.deffered_advance_request(self.reason)

        return {'type': 'ir.actions.act_window_close'}
