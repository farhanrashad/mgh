# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    expense_id = fields.Many2one('hr.expense.sheet', string='Expense Claim')
    