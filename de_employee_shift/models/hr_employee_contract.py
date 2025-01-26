# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class HrEmployeeContract(models.Model):
    _inherit = 'hr.contract'

    shift_schedule = fields.One2many('hr.shift.schedule', 'rel_hr_schedule', string="Shift Schedule", help="Shift schedule")
    working_hours = fields.Many2one('resource.calendar', string='Working Schedule', help="Working hours")
    department_id = fields.Many2one('hr.department', string="Department", help="Department",
                                    required=True)


class HrSchedule(models.Model):
    _name = 'hr.shift.schedule'
    _rec_name = 'hr_shift'

    start_date = fields.Datetime(string="Date From", required=True, help="Starting date for the shift")
    end_date = fields.Datetime(string="Date To", required=True, help="Ending date for the shift")
    rel_hr_schedule = fields.Many2one('hr.contract')
    employee_id = fields.Many2one(related='rel_hr_schedule.employee_id')
    department_id = fields.Many2one(related='rel_hr_schedule.department_id')
    hr_shift = fields.Many2one('resource.calendar', string="Shift", required=True, help="Shift")
    company_id = fields.Many2one('res.company', string='Company', help="Company")
    shift_type = fields.Selection(related='hr_shift.shift_type')

    

    
    def write(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).write(vals)

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).create(vals)

    def _check_overlap(self, vals):
        if vals.get('start_date', False) and vals.get('end_date', False):
            shifts = self.env['hr.shift.schedule'].search([('rel_hr_schedule', '=', vals.get('rel_hr_schedule'))])
            for each in shifts:
                if each != shifts[-1]:
                    if str(each.end_date ) >= str(vals.get('start_date')) or str(each.start_date) >= str(vals.get('start_date')):
                        raise UserError(_('The dates may not overlap with one another.'))
            if str(vals.get('start_date')) > str(vals.get('end_date')):
                raise UserError(_('Start date should be less than end date.'))
        return True

