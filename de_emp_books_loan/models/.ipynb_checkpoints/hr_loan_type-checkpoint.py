# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HREmployeeLoan(models.Model):
    _name = "hr.employee.loan.type"
    _description = "Employee Loan Type"

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('de_emp_books_loan.default_loan_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()
    
    @api.model
    def _default_journal_id(self):
        journal_id = self.env['ir.config_parameter'].sudo().get_param('de_emp_books_loan.default_loan_journal_id')
        return self.env['account.journal'].browse(int(journal_id)).exists()
    
    
    active = fields.Boolean(default=True)
    name = fields.Char(required=True, default='New', Copy=False)
    code = fields.Char(required=True, help="Code is added automatically in the display name of every subscription.")
    description = fields.Text(string="Terms and Conditions")
    
    condition_installment_min = fields.Integer(string='Min. Installment(s)', default=1, help="The minimum installments for loan.")
    condition_installment_max = fields.Integer(string='Max. Installment(s)', default=12, help="The maximum installments for loan.")

    amount_select = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fix', 'Fixed Amount'),
        ('code', 'Python Code'),
    ], string='Amount Type', index=True, required=True, default='fix', help="The computation method for the rule amount.")
    amount_fix = fields.Float(string='Fixed Amount', digits='Payroll')
    amount_percentage = fields.Float(string='Percentage (%)', digits='Payroll Rate',
        help='For example, enter 50.0 to apply a percentage of 50%')
    amount_python_compute = fields.Text(string='Python Code',
        default='''
                    # Available variables:
                    #----------------------
                    # loan: object containing the loans
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # Note: returned value have to be set in the variable 'result'

                    result = contract.wage * 0.10''')
    amount_percentage_base = fields.Char(string='Percentage based on', help='result will be affected to a variable')
    
    
    product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('type', '=', 'service')]", company_dependent=True, check_company=True, default=_default_product_id)
        
    journal_id = fields.Many2one('account.journal', string="Accounting Journal", required=True, domain="[('type', '=', 'purchase')]", company_dependent=True, check_company=True,default=_default_journal_id)
    company_id = fields.Many2one('res.company', string="Company", default=lambda s: s.env.company, required=True)
    
    filter_domain = fields.Char(string='Domain', help="If present, this domain will satisfy the loan eligibility.")
    employee_model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', compute='_compute_hr_employee_model')
    loan_type_doc_ids = fields.One2many('hr.loan.type.doc', 'loan_type_id', string='Loan Documents', copy=False )
    
    description = fields.Html()



    def _compute_hr_employee_model(self):
        self.employee_model_id = self.env.ref('hr.model_hr_employee').id
    
    def _compute_loan(self, localdict):
        """
        :param localdict: dictionary containing the current computation environment
        :return: returns a tuple (amount, qty, rate)
        :rtype: (float, float, float)
        """
        self.ensure_one()
        if self.amount_select == 'fix':
            try:
                return self.amount_fix or 0.0, 100.0
            except Exception as e:
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).\nError: %s') % (self.name, self.code, e))
        if self.amount_select == 'percentage':
            try:
                return (float(safe_eval(self.amount_percentage_base, localdict)),
                        self.amount_percentage or 0.0)
            except Exception as e:
                raise UserError(_('Wrong percentage base or quantity defined for salary rule %s (%s).\nError: %s') % (self.name, self.code, e))
        else:  # python code
            try:
                safe_eval(self.amount_python_compute or 0.0, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), localdict.get('result_rate', 100.0)
            except Exception as e:
                raise UserError(_('Wrong python code defined for salary rule %s (%s).\nError: %s') % (self.name, self.code, e))
                
                
class HRLoanTypeDoc(models.Model):
    _name = "hr.loan.type.doc"
    _order = 'sequence, id'
    _description = 'Loan Eligibility Documents'
    
    name = fields.Char(required=True, string='Name')
    sequence = fields.Integer(required=True, default=5, )
    loan_type_id = fields.Many2one('hr.employee.loan.type', string='Loan Type', readonly=True,)
    is_required = fields.Boolean(string='Required')


