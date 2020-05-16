from odoo import api, fields, models

class SubTasksLine(models.Model):
    _name = 'sub.tasks.line'
    _description = 'this is sub task model'

    title = fields.Char(string='Title')
    project_subtask = fields.Many2one('con.projects', string='Project')
    assign_to = fields.Many2one('res.users', string='Assign to')
    planned_hours = fields.Integer(string='Planned Hours')
    remaining_hours = fields.Integer(string='Remaining Hours')
    stage_subtask = fields.Char(string='Stage')
    progress = fields.Char(string='Progress')
    sub_task_ref = fields.Many2one('job.order', string='ref parent')