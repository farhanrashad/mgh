# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date



class NoteNote(models.Model):
    _inherit = 'note.note'
    
    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade', index=True, copy=False)
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade', index=True, copy=False, domain="[('project_id', '=', project_id)]")
