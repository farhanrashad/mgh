# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    input_line_ids = fields.One2many(compute='_compute_input_line_ids', store=True, readonly=False,
                                     )
    hr_employee_loan_lines = fields.One2many(
        'hr.employee.loan.line', 'payslip_id', string='Installments',
        help="Installments to reimburse to employee.",)
    installments_count = fields.Integer(compute='_compute_installments_count')
    
    @api.depends('hr_employee_loan_lines', 'hr_employee_loan_lines.payslip_id')
    def _compute_installments_count(self):
        for payslip in self:
            payslip.installments_count = len(payslip.mapped('hr_employee_loan_lines'))
            
    @api.onchange('input_line_ids')
    def _onchange_input_line_ids(self):
        #loan_type = self.env.ref('de_emp_books_loan.loan_other_input', raise_if_not_found=False)
        loan_types = self.env['hr.employee.loan.type'].search([('active','=',True)])
        if not self.input_line_ids.filtered(lambda line: line.input_type_id in loan_types.input_type_id):
            self.hr_employee_loan_lines.write({'payslip_id': False})

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        res = super()._onchange_employee()
        if self.state == 'draft':
            self.hr_employee_loan_lines = self.env['hr.employee.loan.line'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'done'),
                ('date_due', '<=', self.date_to),
            ])
            #loan_line_ids = self.env['hr.employee.loan.line'].search([('employee_id','=',self.employee_id.id),('date_due','<=',self.date_to),('state','=','done')])
            #for line in loan_line_ids:
            #    line.write({
            #        'payslip_id':self.id,
            #    })

        return res
    
    
    @api.depends('hr_employee_loan_lines')
    def _compute_input_line_ids(self):
        #loan_type = self.env.ref('de_emp_books_loan.loan_other_input', raise_if_not_found=False)
        loan_types = self.env['hr.employee.loan.type'].search([('active','=',True)])
        for payslip in self:
            total = sum(payslip.hr_employee_loan_lines.mapped('amount_emi'))
            if not total or not loan_types:
                payslip.input_line_ids = payslip.input_line_ids
                continue
            #lines_to_keep = payslip.input_line_ids.filtered(lambda x: x.input_type_id != loan_type)
            lines_to_keep = payslip.input_line_ids.filtered(lambda x: x.input_type_id not in loan_types.input_type_id)
            input_lines_vals = [(5, 0, 0)] + [(4, line.id, False) for line in lines_to_keep]
            for loan_type in loan_types:
                total = sum(payslip.hr_employee_loan_lines.employee_loan_id.filtered(lambda loan: loan.loan_type_id.id == loan_type.id).loan_line.mapped('amount_emi'))
                input_lines_vals.append((0, 0, {
                    'amount': total,
                    'input_type_id': loan_type.input_type_id.id
                }))
            payslip.update({'input_line_ids': input_lines_vals})
            
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for loan in self.hr_employee_loan_lines:
            loan.set_to_close()
        return res
    
    def open_installments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Refund Installments'),
            'res_model': 'hr.employee.loan.line',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.mapped('hr_employee_loan_lines').ids)],
        }