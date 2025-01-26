# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError



class Hr(models.Model):
    _inherit = 'hr.payslip'

    
    def action_generate_entry(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for payslip in self:
            contract=self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id),('state','=','open')], limit=1)
            if not contract:
                contract=self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id)], limit=1)   
            move_dict = {
                  #'name': payslip.name,
                  'journal_id': payslip.journal_id.id,
                  'date': payslip.date_to,
                  'partner_id': payslip.employee_id.address_home_id.id,
                  'state': 'draft',
                       }
                            #step2:debit side entry
            for rule in payslip.line_ids:
                if rule.amount !=0:
                    for cost_center in contract.cost_center_information_line:
                        if cost_center.percentage_charged > 0:
                            credit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_credit','=',True)], limit=1)
                            if not credit_account:
                                credit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('company_id','=', payslip.employee_id.company_id.id),('ora_credit','=',True)], limit=1)

                            if credit_account:
                                #if account.ora_credit== True:
                                credit_line = (0, 0, {
                                        'name': rule.name,
                                        'ora_account_code':  str(payslip.employee_id.company_id.segment1)+'.000.'+str(credit_account.code)+'.'+str(payslip.employee_id.work_location_id.location_code if payslip.employee_id.work_location_id.location_code else '00')+'.00',
                                        'partner_id': payslip.employee_id.address_home_id.id,
                                        'debit': 0.0,
                                        'credit': abs((rule.amount/100)* cost_center.percentage_charged),
    #                                     'analytic_account_id': cost_center.cost_center.id,
                                        'account_id': credit_account.id,
                                             })
                                line_ids.append(credit_line)
                                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
                            debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True),('emp_type','=',payslip.employee_id.emp_type),('grade_type_id','=',payslip.employee_id.grade_type.id)], limit=1)
                            
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True),('emp_type','=',payslip.employee_id.emp_type)], limit=1)    
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True),('emp_type','=',payslip.employee_id.emp_type),('grade_type_id','=',payslip.employee_id.grade_type.id)], limit=1)
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True)], limit=1)
                            if not debit_account:
                                debit_account=self.env['account.account'].search([('salary_rule_id','in', rule.salary_rule_id.ids),('company_id','=', payslip.employee_id.company_id.id),('ora_debit','=',True)], limit=1)
                            if debit_account:
                                extra_deduct_amount = 0   
                                if rule.salary_rule_id.ora_extra_from_ded==True:
                                    for e_rule in payslip.line_ids:
                                        if e_rule.salary_rule_id.ora_extra_to_ded==True:
                                            extra_deduct_amount += e_rule.amount
                                debit_line = (0, 0, {
                                        'name': rule.name,
                                        'ora_account_code':  str(payslip.employee_id.company_id.segment1)+'.'+str(cost_center.cost_center.code)+'.'+str(debit_account.code)+'.'+str(payslip.employee_id.work_location_id.location_code if payslip.employee_id.work_location_id.location_code else '00')+'.00',
                                        'partner_id': payslip.employee_id.address_home_id.id,
                                        'debit': abs(((rule.amount/100)* cost_center.percentage_charged)-((extra_deduct_amount/100)*cost_center.percentage_charged)),
                                        'credit': 0.0,
                                        'analytic_account_id': cost_center.cost_center.id,
                                        'account_id': debit_account.id,
                                             })
                                line_ids.append(debit_line)
                                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            account=self.env['account.account'].search([], limit=1)
           
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            payslip.update({
                'move_id': move.id,
            })

    
    
    
    
