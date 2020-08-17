from odoo import api, fields, models


class SubTasksLine(models.Model):
    _name = 'sub.tasks.line'
    _description = 'SubTask Line'
    _rec_name = 'title'

    title = fields.Char(string='Title', required=True)
    project_sub_task = fields.Many2one(comodel_name='con.projects', string='Project')
    assign_to = fields.Many2one(comodel_name='res.users', string='Assign to')
    planned_hours = fields.Integer(string='Planned Hours')
    remaining_hours = fields.Integer(string='Remaining Hours')
    stage_sub_task = fields.Char(string='Stage')
    progress = fields.Char(string='Progress')
    sub_task_ref = fields.Many2one(comodel_name='job.order', string='ref parent')
