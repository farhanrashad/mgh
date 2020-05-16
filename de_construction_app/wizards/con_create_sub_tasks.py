from odoo import api, fields, models

class CreateSubtsk(models.Model):
    _name = 'create.subtask'
    _description = 'Create SubTask'



    user_id = fields.Many2one(comodel_name="res.users", string="", required=False, )
    task_id = fields.Char(string="", required=False, )
    name = fields.Char(string="", required=False, )
    planned_hours = fields.Datetime(string="", required=False, )
    create_id = fields.Many2one('job.order', 'Project Subtask User')
