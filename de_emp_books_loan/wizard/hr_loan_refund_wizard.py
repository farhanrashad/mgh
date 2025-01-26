# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class HREmployeeLoanRefundWizard(models.Model):
    _name = 'hr.employee.loan.refund.wizard'
    _description = 'Employee Loan Refund Wizard'
    
    @api.model
    def _default_journal_id(self):
        journal_id = self.env['ir.config_parameter'].sudo().get_param('de_emp_books_loan.default_loan_journal_id')
        return self.env['account.journal'].browse(int(journal_id)).exists()
    
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False, compute='_compute_amount')
    date_refund = fields.Date(string="Refund Date", required=True, default=fields.Date.context_today)
    communication = fields.Char(string="Memo", store=True, readonly=False, compute='_compute_communication')
    company_id = fields.Many2one('res.company', )
    currency_id = fields.Many2one('res.currency', string='Currency')
    employee_loan_id = fields.Many2one('hr.employee.loan',string='Loan',)
    refund_type = fields.Selection([
        ('refund', 'Refund Invoice'),
        ('writeoff', 'Write-off'),
    ], string='Refund Type', copy=False, index=True,  default='refund', help="Refund type for loan adjustment")
    
    reason = fields.Char(string='Reason', required=True)

    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type','=','purchase')]", default=_default_journal_id)
    
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", copy=False, domain="[('deprecated', '=', False), ('company_ids', 'in', company_id)]")
    writeoff_label = fields.Char(string='Journal Item Label', default='Write-Off', help='Change label of the counterpart that will hold the payment difference')
        
    @api.model
    def default_get(self, fields):
        res = super(HREmployeeLoanRefundWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        employee_loan_id = self.env['hr.employee.loan'].browse(self._context.get('active_ids',[]))
        #refund_model = self.env.context.get('hr_employee_loan_refund_model')
        #if refund_model == 'hr.employee.loan':
        res.update({
            'employee_loan_id': active_ids[0] if active_ids else False,
            'journal_id': employee_loan_id.loan_type_id.journal_id.id,
            'amount': employee_loan_id.amount_residual,
            'communication': employee_loan_id.ref,
            'company_id': employee_loan_id.company_id.id,
        })
        return res
    
    def _compute_communication(self):
        self.communication = self.employee_loan_id.ref
        
    def _compute_amount(self):
        t = 0
        
    def create_refund(self):
        self.ensure_one()
        refund = False
        if self._context.get('refund_invoice', False):
            refund = True
            #self.employee_loan_id.action_refund_loan(refund=True, self.amount, self.reason)
        #else:
        self.employee_loan_id.action_refund_loan(refund, self.amount, self.date_refund, self.reason)
            
        return {'type': 'ir.actions.act_window_close'}