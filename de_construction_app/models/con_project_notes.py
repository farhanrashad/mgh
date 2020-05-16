# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class ProjectNotes(models.Model):
    _name = 'project.notes'
    _description = 'this is project model'
    _rec_name = 'note'

    tag_ids = fields.Char(string='Tags')
    task_id = fields.Many2one('job.order',string='Task/ Job Order')
    project_id = fields.Many2one('con.projects',string='Construction Project')
    user_id = fields.Many2one('res.users',string='Responsible User')
    state = fields.Selection([
        ('new', 'New'),
        ('meeting_mint', 'Meeting Minutes'),
        ('notes', 'Notes'),
        ('todo', 'Todo'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='new')
    note = fields.Html(string="Description" )
