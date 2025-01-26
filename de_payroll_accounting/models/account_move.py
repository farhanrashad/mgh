# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class AccountAccounts(models.Model):
    _inherit = 'account.move'        
    
    def action_post_payroll_data(self):
        analytic_account_list = []
        credit_account_list = []
        debit_account_list = []
        final_gl_account_list = []
        move_lines = 0
        journala = 0
        payslip = 0
        ora_date = fields.date.today()
        for line in self:
            ledgerna = line.company_id.ledger_id
            journala = line.journal_id.id
            ora_date = line.date
            payslip = self.env['hr.payslip'].search([('move_id', '=', line.id)], limit=1)
            move_lines = self.env['account.move.line'].search(
                [('company_id', '=', line.company_id.id), ('date', '>=', line.date),('date','<=',line.date),('journal_id.ora_ledger_label','=','Payroll')])
        for mv in move_lines:
            if mv.account_id.ora_credit==True:  
                credit_account_list.append(mv.account_id.id)
            if mv.account_id.ora_debit==True:  
                debit_account_list.append(mv.account_id.id)                
            analytic_account_list.append(mv.analytic_account_id.id) 
                
        uniq_analytic_account_list = set(analytic_account_list)
        uniq_credit_account_list = set(credit_account_list)
        uniq_debit_account_list = set(debit_account_list)
        mv_account_code = 0
        for credit_account in uniq_credit_account_list:
            credit_total = 0
            mv_account_code = 0
            company = 0
            for mv_line in move_lines:
                if credit_account == mv_line.account_id.id:
                    credit_total +=  mv_line.credit
                    company = mv_line.move_id.company_id.id
            if  credit_total > 0:  
                ora_credit_account = self.env['account.account'].search([('id','=', credit_account)], limit=1)    
                code_spliting = ora_credit_account.code.split('.')      
                ora_ledger = self.env['ora.ledger.report'].create({
                        'company_id':  company, 
                        'journal_id': journala,
                        'payslip_run_id': payslip.payslip_run_id.id,                      
                        'account_id': credit_account, 
                        'control_account_id': self.env['controlled.account'].search([('code','=',code_spliting[0] )]).id , 
                        'date':  ora_date,
                        'debit':  0,
                        'credit': credit_total,
                })
        debit_mv_account_code = 0        
        for analytic in uniq_analytic_account_list:            
            for debit_account in uniq_debit_account_list:
                debit_total = 0 
                debit_mv_account_code = 0
                for mv_line in move_lines:
                    if analytic == mv_line.analytic_account_id.id and debit_account == mv_line.account_id.id:
                        debit_total +=  mv_line.debit
                        debit_mv_account_code = mv_line.ora_account_code
                if  debit_total > 0: 
                    ora_debit_account = self.env['account.account'].search([('id','=', debit_account)], limit=1)    
                    code_spliting = ora_debit_account.code.split('.')   
                    ora_ledger = self.env['ora.ledger.report'].create({
                        'company_id':  company, 
                        'journal_id': journala, 
                        'payslip_run_id': payslip.payslip_run_id.id,  
                        'analytic_account_id':  analytic,                        
                        'account_id': debit_account, 
                        'control_account_id': self.env['controlled.account'].search([('code','=',code_spliting[0])], limit=1).id , 
                        'date':  ora_date,
                        'debit':  debit_total,
                        'credit': 0,
                    }) 
    
    
    
    
