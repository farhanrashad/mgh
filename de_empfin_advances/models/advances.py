# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class EmployeeAdvanceType(models.Model):
    _name = "hr.employee.advance.type"
    _description = "Employee Advance Type"
    _order = "sequence"

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(default=1)
    product_id = fields.Many2one('product.product', string='Product', readonly=False, required=True, tracking=True, domain="[('type', '=', 'service')]", ondelete='restrict')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain="[('type','=','purchase')]")
    
class EmployeeAdvance(models.Model):

    _name = "hr.employee.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Advance"
    _order = "date desc, id desc"
    _check_company_auto = True
    
    name = fields.Char('Description', compute='_compute_from_product_id_company_id', store=True, required=True, copy=True,
        )
    
    ref = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

        
    date = fields.Date(readonly=True,     required=True, default=fields.Date.context_today, string="Request Date")
    date_due = fields.Date(readonly=True,     required=True, default=fields.Date.context_today, string="Due Date")

    accounting_date = fields.Date(readonly=True,     default=fields.Date.context_today, string="Accounting Date")
    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee", store=True, required=True, readonly=False, tracking=True,
                                  check_company=True)
    manager_user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False,    tracking=True, domain=lambda self: [('groups_id', 'in', self.env.ref('de_empfin_advances.group_hr_advance_team_approver').id)])
    user_id = fields.Many2one('res.users', string='Requested By', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: [('groups_id', 'in', self.env.ref('de_empfin_advances.group_hr_advance_user').id)])


    manager_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id')
    department_id = fields.Many2one('hr.department', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, string='Department',
                                    )
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.company.currency_id)
    
    advance_type_id = fields.Many2one('hr.employee.advance.type', string='Advance Type', readonly=True, copy=False,
                                      )
    product_id = fields.Many2one('product.product', string='Product', related='advance_type_id.product_id')
    product_uom_id = fields.Many2one('uom.uom', string='UOM', related='advance_type_id.product_id.uom_id')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submit', 'Submitted'),
        ('approved', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('refused', 'Refused')
    ], string='Status', copy=False, index=True,  compute='_compute_state', store=True, default='draft', help="Status of the Avances.")
    
    amount = fields.Monetary("Amount", currency_field='currency_id', tracking=True, required=True, readonly=True, copy=False,
                             )
    description = fields.Text('Notes...', readonly=True, )
    
    address_id = fields.Many2one('res.partner', compute='_compute_from_employee_id', store=True, readonly=False, copy=True, string="Employee Home Address", check_company=True, )
    
    applicable_amount = fields.Monetary('Applicable Amount', compute='compute_from_job',readonly=True, store=True, copy=False)
    allow_exceeded_limit = fields.Boolean('Overwrite Exceeded Limit')
    
    journal_id = fields.Many2one('account.journal', compute='_compute_journal_from_advance_type', store=True)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)
    payment_state = fields.Selection('Payment State', related='account_move_id.payment_state')
    can_reset = fields.Boolean('Can Reset', compute='_compute_can_reset')

    amount_ded = fields.Monetary("Deduction", currency_field='currency_id', readonly=True, copy=False, compute='_compute_advance_balance' )
    balance = fields.Monetary("Balance", currency_field='currency_id', readonly=True, copy=False, compute='_compute_advance_balance' )
    
    @api.depends('payment_state')
    def _compute_state(self):
        for adv in self:
            if adv.payment_state == 'in_payment':
                adv.state = 'done'
    
    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].get('hr.employee.advance') or ' '
        res = super(EmployeeAdvance, self).create(vals)
        return res
    
    
    def _compute_can_reset(self):
        is_advance_user = self.user_has_groups('de_empfin_advances.group_hr_advance_team_approver')
        for adv in self:
            adv.can_reset = is_advance_user if is_advance_user else adv.employee_id.user_id == self.env.user
            
    def unlink(self):
        for adv in self:
            if adv.state not in ['draft']:
                raise UserError(_('You cannot delete a posted or approved request.'))
        return super(EmployeeAdvance, self).unlink()
    
    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for adv in self:
            adv.address_id = adv.employee_id.sudo().address_home_id
            adv.department_id = adv.employee_id.department_id
            #adv.job_id = adv.employee_id.job_id
            adv.manager_user_id = adv.employee_id.advance_manager_id or adv.employee_id.parent_id.user_id
            
    
    @api.depends('job_id')
    def compute_from_job(self):
        amount = 0
        for adv in self:
            if adv.job_id.advance_limit_method == 'percentage':
                amount = adv.employee_id.contract_id.wage * (adv.job_id.amount / 100)
            else:
                amount = adv.job_id.fixed_amount
            adv.applicable_amount = amount
        
    @api.depends('advance_type_id')
    def _compute_journal_from_advance_type(self):
        for adv in self:
            adv.journal_id = adv.advance_type_id.journal_id
            
    def action_submit_advance(self):
        if self.amount ==0:
            raise UserError(_("The request cannot submit for 0 amount."))
        elif self.amount < 0:
            raise UserError(_("The request cannot submit for negative amount."))
        if not self.allow_exceeded_limit:
            if self.amount > self.applicable_amount:
                raise UserError(_("The request cannot submit for higher than available limit."))
                
        self.write({'state': 'submit'})
        self.activity_update()
        
    
    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']
    
    def activity_update(self):
        for adv in self.filtered(lambda adv: adv.state == 'submit'):
            self.activity_schedule(
                'de_empfin_advances.mail_act_advance_approval',
                user_id=adv.sudo()._get_responsible_for_approval().id or self.env.user.id)
        self.filtered(lambda hol: hol.state == 'approve').activity_feedback(['de_empfin_advances.mail_act_advance_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['de_empfin_advances.mail_act_advance_approval'])
        
    
    def approve_advance(self):
        if not self.user_has_groups('de_empfin_advances.group_hr_advance_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve advances"))
        elif not self.user_has_groups('de_empfin_advances.group_hr_advance_manager'):
            current_managers = self.employee_id.advance_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own advance request"))

            if not self.env.user in current_managers and not self.user_has_groups('de_empfin_advances.group_hr_advance_user') and self.employee_id.advance_manager_id != self.env.user:
                raise UserError(_("You can only approve your department advances"))
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no advance requests to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        state = ''
        filtered_advance = self.filtered(lambda s: s.state in ['submit', 'draft'])
        if not filtered_advance:
            return notification
        for adv in filtered_advance:
            adv.write({
                'state': 'approved', 
                'user_id': adv.user_id.id or self.env.user.id
            })
        notification['params'].update({
            'title': _('The advance requests were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
            
        self.activity_update()
        return notification
    
    def _compute_advance_balance(self):
        for line in self:
            payslip_id = self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('date_from','<=',line.date),('date_to','>=',line.date),('state','=','done')],limit=1)
            payslip_input_id = self.env['hr.payslip.input']            
            domain = [('payslip_id', '=', payslip_id.id)]

            where_query = payslip_input_id._where_calc(domain)
            payslip_input_id._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.amount_ded = self.env.cr.fetchone()[0] or 0.0
            line.balance = line.amount - line.amount_ded
    
    
    
    def reset_advance_request(self, reason):
        if not self.can_reset:
            raise UserError(_("Only HR Officers or the concerned employee can reset to draft."))
        self.write({'state': 'draft'})
        self.activity_update()
        return True
    
    def refuse_advance(self, reason):
        if not self.user_has_groups('de_empfin_advances.group_hr_advance_team_approver'):
            raise UserError(_("Only Managers and HR Officers can refuse advances"))
        elif not self.user_has_groups('de_empfin_advances.group_hr_advance_manager'):
            current_managers = self.employee_id.advance_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot refuse your own advance request"))

            if not self.env.user in current_managers and not self.user_has_groups('de_empfin_advances.group_hr_advance_user') and self.employee_id.advance_manager_id != self.env.user:
                raise UserError(_("You can only refuse your department advance requests"))

        self.write({'state': 'cancel'})
        for adv in self:
            adv.message_post_with_view('de_empfin_advances.hr_advance_template_refuse_reason', values={'reason': reason, 'is_sheet': True, 'name': adv.name})
        self.activity_update()
        
        
    def action_create_bill(self):
        if not self.journal_id.id:
            raise UserError(_("Accounting Journal is missing"))
            
        if not self.address_id.id:
            raise UserError(_("Respective partner is missing for employee"))
            
        res = self._create_bill()
        self.update({
            'state' : 'post',
        })
        #return self.action_subscription_invoice()
    
    def _create_bill(self):
        invoice = self.env['account.move']
        lines_data = []
        for adv in self:
            lines_data.append([0,0,{
                'name': str(adv.name) + ' ' + str(adv.product_id.name),
                'hr_employee_advance_id': adv.id,
                'price_unit': adv.amount or 0.0,
                'quantity': 1,
                'product_uom_id': adv.product_uom_id.id,
                'product_id': adv.product_id.id,
                'tax_ids': [(6, 0, adv.product_id.supplier_taxes_id.ids)],
                #'analytic_account_id': line.analytic_account_id.id,
                #'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
            }])
        self.account_move_id = invoice.create({
            'move_type': 'in_invoice',
            'invoice_date': fields.Datetime.now(),
            'partner_id': self.address_id.id,
            'currency_id': self.currency_id.id,
            'journal_id': self.journal_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.address_id.property_supplier_payment_term_id.id,
            'narration': self.name,
            'invoice_user_id': self.user_id.id,
            'invoice_line_ids':lines_data,
        })
        self.account_move_id._post()
        return invoice





