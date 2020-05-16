from odoo import api, fields, models



class TimeSheetline(models.Model):
    _name = 'time.sheet.line'
    _description = 'this is time sheet model'

    date_timesheet = fields.Date(string='Date')
    employee_name = fields.Many2one('res.users', string='Employee')
    # name = fields.Text(string='Description')
    time_perioud = fields.Float(string='Duration(Hours(s))')
    time_sheet = fields.Many2one('job.order', string='Ref Parent')
    name = fields.Char(string="Description", required=False, )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
