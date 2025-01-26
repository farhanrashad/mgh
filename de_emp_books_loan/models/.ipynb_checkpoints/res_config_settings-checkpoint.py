# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    loan_default_product_id = fields.Many2one('product.product', 'Loan Product', domain="[('type', '=', 'service')]", config_parameter='de_emp_books_loan.default_loan_product_id', help='Default product used for payment advances')
    loan_default_journal_id = fields.Many2one('account.journal', 'Journal', config_parameter='de_emp_books_loan.default_loan_journal_id', help='Default journal used for loan payments')
    
    interest_default_account_id = fields.Many2one('account.account', 'Interest Account', config_parameter='sale.default_deposit_product_id', help='Default product used for payment advances')
    writeoff_default_account_id = fields.Many2one('account.account', 'Write-Off Account', config_parameter='sale.default_deposit_product_id', help='Default product used for payment advances')



