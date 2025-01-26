# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from odoo.tools.misc import formatLang, format_date, get_lang


class HREmployeeLoanDeferred(models.Model):
    _name = "hr.employee.loan.deferred"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Loan EMI Deferred Request"
    _order = "date desc, id desc"
    _check_company_auto = True
    
    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id
        
    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('de_emp_books_loan.group_hr_loan_user') or self.user_has_groups('account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('de_emp_books_loan.group_hr_loan_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('loan_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]
        return res
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date = fields.Date(readonly=True, required=True, default=fields.Date.context_today, string="Request Date")
    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee", store=True, required=True, readonly=True, tracking=True,    default=_default_employee_id, domain=lambda self: self._get_employee_id_domain(), check_company=True)
    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False,    tracking=True, domain=lambda self: [('groups_id', 'in', self.env.ref('de_emp_books_loan.group_hr_loan_team_approver').id)])
    department_id = fields.Many2one('hr.department', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, string='Department' )
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,    default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,    default=lambda self: self.env.company.currency_id)
    
    employee_loan_id = fields.Many2one('hr.employee.loan', string='Loan', readonly=True, copy=False,    domain="[('employee_id','=',employee_id),('state','=','done')]")
    employee_loan_line_id = fields.Many2one('hr.employee.loan.line', string='Installment', readonly=True, domain="[('employee_loan_id','=',employee_loan_id)]", compute='_compute_current_installment')
                                       
    amount_loan = fields.Monetary("Amount", currency_field='currency_id', store=True, readonly=True, copy=False, compute='_compute_all_loan' )
    amount_residual_loan = fields.Monetary("Residual Amount", currency_field='currency_id', store=True, readonly=True, copy=False, compute='_compute_all_loan' )
    
    deferred_period = fields.Integer(string='Deferred Period', default=1, required=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submit', 'Submitted'),
        ('done', 'Approved'),
        ('cancel', 'Refused')
    ], string='Status', copy=False, index=True,  default='draft', help="Status of request.")
    
    description = fields.Text('Notes...', readonly=True)
    

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.employee.loan.deferred') or ' '
        res = super(HREmployeeLoanDeferred, self).create(vals)
        return res
    
    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for loan in self:
                loan.employee_id = self.env.user.with_company(loan.company_id).employee_id
                
    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for loan in self:
            loan.department_id = loan.employee_id.department_id
            loan.user_id = loan.employee_id.parent_id.user_id
    
    @api.depends('employee_loan_id')
    @api.onchange('employee_loan_id')
    def _compute_current_installment(self):
        loan_line_id = self.env['hr.employee.loan.line'].search([('employee_id','=',self.employee_id.id),('employee_loan_id','=',self.employee_loan_id.id),('state','=','done')],order="date_due",limit=1)
        self.employee_loan_line_id = loan_line_id.id
            
    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']
    
    @api.depends('employee_loan_id')
    def _compute_all_loan(self):
        for loan in self:
            loan.amount_loan = sum(loan.employee_loan_id.loan_line.mapped('amount_total'))
            loan.amount_residual_loan = 0
    # --------------------------------------------
    # Mail Thread
    # --------------------------------------------

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        email_address = email_split(msg_dict.get('email_from', False))[0]

        employee = self.env['hr.employee'].search([
            '|',
            ('work_email', 'ilike', email_address),
            ('user_id.email', 'ilike', email_address)
        ], limit=1)

        loan_description = msg_dict.get('subject', '')

        if employee.user_id:
            company = employee.user_id.company_id
            currencies = company.currency_id | employee.user_id.company_ids.mapped('currency_id')
        else:
            company = employee.company_id
            currencies = company.currency_id

        if not company:  # ultimate fallback, since company_id is required on expense
            company = self.env.company

        # The expenses alias is the same for all companies, we need to set the proper context
        # To select the product account
        self = self.with_company(company)

        product, price, currency_id, loan_description = self._parse_expense_subject(loan_description, currencies)
        vals = {
            'employee_id': employee.id,
            'name': loan_description,
            'loan_type': price,
            'amount': product.id if product else None,
            'installments': product.uom_id.id,
            'quantity': 1,
            'company_id': company.id,
            'currency_id': currency_id.id
        }

        account = product.product_tmpl_id._get_product_accounts()['expense']
        if account:
            vals['account_id'] = account.id

        expense = super(HrExpense, self).message_new(msg_dict, dict(custom_values or {}, **vals))
        self._send_expense_success_mail(msg_dict, expense)
        return expense
    
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'approve':
            return self.env.ref('de_emp_books_loan.mt_loan_approved')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('de_emp_books_loan.mt_loan_refused')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('de_emp_books_loan.mt_loan_paid')
        return super(HREmployeeLoanDeferred, self)._track_subtype(init_values)

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        res = super(HREmployeeLoanDeferred, self)._message_auto_subscribe_followers(updated_values, subtype_ids)
        if updated_values.get('employee_id'):
            employee = self.env['hr.employee'].browse(updated_values['employee_id'])
            if employee.user_id:
                res.append((employee.user_id.partner_id.id, subtype_ids, False))
        return res

    
    def activity_update(self):
        for adv in self.filtered(lambda adv: adv.state == 'submit'):
            self.activity_schedule(
                'de_emp_books_loan.mail_act_loan_approval',
                user_id=adv.sudo()._get_responsible_for_approval().id or self.env.user.id)
        self.filtered(lambda hol: hol.state == 'approve').activity_feedback(['de_emp_books_loan.mail_act_loan_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['de_emp_books_loan.mail_act_loan_approval'])
                
    # --------------------------------------------
    # Action Buttons
    # --------------------------------------------
    def action_submit_request(self):
        if self.deferred_period <=0:
            raise UserError(_("The request cannot submit with 0 or less period."))
                
        self.write({'state': 'submit'})
        self.activity_update()
    
    def reset_request(self):
        if not self.can_reset:
            raise UserError(_("Only HR Officers or the concerned employee can reset to draft."))
        self.write({'state': 'draft'})
        self.activity_update()
        return True
        
    def approve_request(self):
        if not self.user_has_groups('de_emp_books_loan.group_hr_loan_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve loan"))
        elif not self.user_has_groups('de_emp_books_loan.group_hr_loan_manager'):
            current_managers = self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own request"))

            if not self.env.user in current_managers and not self.user_has_groups('de_emp_books_loan.group_hr_loan_user') and self.employee_id.parent_id.user_id != self.env.user:
                raise UserError(_("You can only approve your department requests"))
        
        loan_line_ids = self.env['hr.employee.loan.line'].search([('employee_id','=',self.employee_id.id),('employee_loan_id','=',self.employee_loan_id.id),('state','=','done')],order="date_due",limit=self.deferred_period)
        date_start = False
        date_end = False
        date_due = False
        principal = 0.0
        #for loan in loan_line_ids:
        #    loan.write({
        #        'state': 'cancel'
        #    })
        #    date_start = loan.date_end
            #principal = loan.amount_principal
            #date_end = date_start + relativedelta(months=1,days=-1)
            #date_due = date_start + relativedelta(months=1)
       
        # cancel entries
        loan_line_ids = self.env['hr.employee.loan.line'].search([('employee_id','=',self.employee_id.id),('state','=','done'),('employee_loan_id','=',self.employee_loan_id.id)],order="date_due", limit=self.deferred_period)
        for line in loan_line_ids:
            self.env['hr.employee.loan.line'].create({
                'employee_loan_id':line.employee_loan_id.id,
                'employee_id':line.employee_loan_id.employee_id.id,
                'date': line.date,
                'date_end': line.date_end,
                'date_due': line.date_due,
                'currency_id': line.employee_loan_id.currency_id.id,
                'amount': line.amount,
                'amount_interest': line.amount_interest,
                'amount_emi': line.amount_emi,
                'amount_total':line.amount_total,
                'state':'cancel',
            })
            
            
        # Revised Loan Lines
        loan_rv_line_ids = self.env['hr.employee.loan.line'].search([('employee_id','=',self.employee_id.id),('state','=','done'),('employee_loan_id','=',self.employee_loan_id.id)],order="date_due")
        
        
        
        cumulated_bal = 0.0
        
        for line in loan_rv_line_ids:
            date_start = line.date + relativedelta(months=self.deferred_period)
            date_end = date_start + relativedelta(months=self.deferred_period,days=-1)
            date_due = date_start + relativedelta(months=self.deferred_period)
            line.write({
            #   'amount_principal': principal,
                'date': date_start,
                'date_end': date_end,
                'date_due': date_due,
            })    
            #principal -= line.amount
            date_start = line.date_end
            
    
    def action_refuse_loan(self, reason):
        if not self.user_has_groups('de_emp_books_loan.group_hr_loan_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve loan"))
        elif not self.user_has_groups('de_emp_books_loan.group_hr_loan_manager'):
            current_managers = self.employee_id.loan_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot refuse your own request"))

            if not self.env.user in current_managers and not self.user_has_groups('de_emp_books_loan.group_hr_loan_user') and self.employee_id.loan_manager_id != self.env.user:
                raise UserError(_("You can only refuse your department loan requests"))

        self.write({'state': 'refused'})
        for loan in self:
            loan.message_post_with_view('de_emp_books_loan.hr_employee_loan_template_refuse_reason', values={'reason': reason, 'is_sheet': True, 'name': loan.name})
        self.activity_update()
        
    def action_create_bill(self):
        if not self.journal_id.id:
            raise UserError(_("Accounting Journal is missing"))
                        
        res = self._create_bill()
        self.update({
            'state' : 'post',
        })


