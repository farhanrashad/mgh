# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class Employee(models.Model):
    _inherit = 'hr.employee'
    
    def _group_hr_advance_user_domain(self):
        group = self.env.ref('de_empfin_advances.group_hr_advance_team_approver', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    advance_manager_id = fields.Many2one(
        'res.users', string='Advance',
        domain=_group_hr_advance_user_domain,
        compute='_compute_advance_manager', store=True, readonly=False,
        help='Select the user responsible for approving "Advances" of this employee.\n'
             'If empty, the approval is done by an Administrator or Approver (determined in settings/users).')

    @api.depends('parent_id')
    def _compute_advance_manager(self):
        for employee in self:
            previous_manager = employee._origin.parent_id.user_id
            manager = employee.parent_id.user_id
            if manager and manager.has_group('de_empfin_advances.group_hr_advance_user') and (employee.advance_manager_id == previous_manager or not employee.advance_manager_id):
                employee.advance_manager_id = manager
            elif not employee.advance_manager_id:
                employee.advance_manager_id = False