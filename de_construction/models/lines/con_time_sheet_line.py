from odoo import api, fields, models


class TimeSheetLine(models.Model):
    _name = 'time.sheet.line'
    _description = 'Time Sheet'

    date_time_sheet = fields.Date(string='Date', required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    time_period = fields.Float(string='Duration(Hours(s))')
    time_sheet = fields.Many2one(comodel_name='job.order', string='Ref Parent')
    name = fields.Char(string='Description')
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account')
