# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError
logger = logging.getLogger(__name__)
import cx_Oracle

class ORALedgerReport(models.Model):
    _name = 'ora.ledger.report'
    _description = 'ORA Ledger Report'

    
    company_id = fields.Many2one('res.company', string='Company')
    journal_id = fields.Many2one('account.journal', string='Journal')
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Batch')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    account_id = fields.Many2one('account.account', string='Account')
    control_account_id = fields.Many2one('controlled.account', string='Control Account')
    date = fields.Date(string='Date')
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    ora_posted = fields.Boolean(string='Post To Oracle')

    def action_posted_on_oracle_payroll(self):
        analytic_account_list = []
        credit_account_list = []
        debit_account_list = []
        final_gl_account_list = []
        move_lines = 0
        total_serial_no = 0
        ledgerna = 0 
        batchid = 0
        batch_name = ''
        for inv in self:
            if inv.ora_posted==False:
                inv_name = inv.account_id.name
                ledger = inv.company_id.ledger_id
                ledger_id = int(ledger)
                currency_code = inv.company_id.currency_id.name
                date_created = fields.date.today().strftime('%d-%b-%Y')
                created_by = -1
                flag = 'A'
                jv_category = 'Odoo Payroll'
                #company code
                segment1 = inv.company_id.segment1
                #cost center
                segment2 = inv.analytic_account_id.code if inv.analytic_account_id else '000'
                code_spliting = inv.account_id.code.split('.')
                #control-account
                segment3 = code_spliting[0]
                #sub account
                segment4 = code_spliting[1]
                segment5 =  '00'
                segment6 =  '00'
                entered_dr = inv.debit
                entered_cr = inv.credit
                accounting_dr = inv.debit
                accountng_cr = inv.credit
                ref1 = 'Odoo' + ' ' + str(inv.journal_id.ora_ledger_label) + ' ' + str(
                            inv.company_id.ledger_id) + '-' + str(
                            inv.date.strftime('%Y')) + '-' + str(
                            inv.date.strftime('%m')) + '-' + str(inv.date.strftime('%d'))
                reference1 = ref1
                ref2 = 'Odoo' + ' ' + str(inv.journal_id.ora_ledger_label) + ' ' + str(
                            inv.company_id.ledger_id) + '-' + str(
                            inv.date.strftime('%Y')) + '-' + str(
                            inv.date.strftime('%m')) + '-' + str(inv.date.strftime('%d'))
                reference2 = ref2
                ref4 = str(inv.payslip_run_id.id)+' ' +str(inv.payslip_run_id.name)
                reference4 = ref4
                ref5 = 'Odoo' + ' ' + str(inv.journal_id.ora_ledger_label)+' '+ str(inv.payslip_run_id.id)+' ' +str(inv.payslip_run_id.name)
                reference5 = ref5
                reference6 = 'Odoo' + ' ' + str(inv.journal_id.ora_ledger_label)+' '+str(inv.journal_id.name)
                ref10 = str(inv.payslip_run_id.id) + ' ' + str(inv.payslip_run_id.name) +' '+str(inv.id)
                reference10 = ref10
                ref21 = str(inv.company_id.ledger_id) + '-' + str(inv.payslip_run_id.id) + '-' + str(inv.id)
                reference21=ref21
                group_uniq_ref = str(inv.company_id.ledger_id) + str(
                                    fields.datetime.now().strftime('%Y%m%d')) + str(
                                    inv.payslip_run_id.id)
                group_id = int(group_uniq_ref)
                period_name = inv.date.strftime('%b-%Y')
                inv_date = inv.date.strftime('%d-%b-%Y')
                conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                cur = conn.cursor()
                statement = 'insert into XX_ODOO_GL_INTERFACE(STATUS,LEDGER_ID, ACCOUNTING_DATE, CURRENCY_CODE,DATE_CREATED,CREATED_BY,ACTUAL_FLAG,USER_JE_CATEGORY_NAME,USER_JE_SOURCE_NAME, SEGMENT1, SEGMENT2, SEGMENT3, SEGMENT4, SEGMENT5, SEGMENT6, ENTERED_CR, ENTERED_DR, ACCOUNTED_CR, ACCOUNTED_DR,REFERENCE1, REFERENCE2, REFERENCE4, REFERENCE5, REFERENCE6, REFERENCE10,REFERENCE21, GROUP_ID, PERIOD_NAME) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21,: 22,:23,: 24,:25,:26,:27,:28,:29)'
                cur.execute(statement,('NEW', ledger_id, inv_date, currency_code, date_created, created_by, flag,  jv_category, 'Odoo',segment1, segment2, segment3, segment4, segment5,segment6, entered_cr, entered_dr, accountng_cr, accounting_dr, reference1, reference2, reference4, reference5, reference6, reference10,reference21, group_id, period_name))
                conn.commit()
                inv.ora_posted = True
    
    
    
    
















