# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class Employee(models.Model):
    _inherit = 'hr.employee'
                
    def compute_loan_installment(self,date_from,date_to):
        loan_line_ids = self.env['hr.employee.loan.line']
        amount = 0
        for emp in self:
            loan_line_ids = self.env['hr.employee.loan.line'].search([('date_due','>=',date_from),('date_due','<=',date_to),('state','=','done')])
            for line in loan_line_ids:
                amount += line.amount_emi
        return amount