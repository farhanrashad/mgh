# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hr_employee_advance_id = fields.Many2one('hr.employee.advance', string='Advance Request', copy=False, help="Advance request where the move line come from")