# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hr_employee_loan_id = fields.Many2one('hr.employee.loan', string='Loan Request', copy=False, help="Loan request where the move line come from")