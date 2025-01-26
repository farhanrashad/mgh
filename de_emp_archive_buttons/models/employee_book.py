
from odoo import fields, models


class InheritedHRExpensePrepayment(models.Model):
    _inherit =  "hr.expense.prepayment"
    
    active = fields.Boolean('Active', default=True)


class InheritedHRExpensePrepaymentLines(models.Model):
    _inherit = "hr.expense.prepayment.line"

    active = fields.Boolean('Active', default=True)

