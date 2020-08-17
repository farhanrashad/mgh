# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class ProjectTaskType(models.Model):
    _name = 'con.project.task.type'
    _description = 'Task Stage'
    _rec_name = 'name'
    _order = 'sequence, id'

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    # def unlink(self):
    #     stages = self
    #     default_project_id = self.env.context.get('default_project_id')
    #     if default_project_id:
    #         shared_stages = self.filtered(lambda x: len(x.project_ids) > 1 and default_project_id in x.project_ids.ids)
    #         tasks = self.env['project.task'].with_context(active_test=False).search([
    #             ('project_id', '=', default_project_id),
    #             ('stage_id', 'in', self.ids)])
    #         if shared_stages and not tasks:
    #             shared_stages.write({'project_ids': [(3, default_project_id)]})
    #             stages = self.filtered(lambda x: x not in shared_stages)
    #     return super(ProjectTaskType, stages).unlink()

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=1)
    project_ids = fields.Many2many('con.projects',
                                   string='Projects',
                                   default=_get_default_project_ids)

    legend_blocked = fields.Char(
        string='Red Label', default=lambda s: _('Blocked'), translate=True, required=True)
    legend_done = fields.Char(
        string='Green Label', default=lambda s: _('Ready for Next Stage'), translate=True, required=True)
    legend_normal = fields.Char(
        string='Grey Label', default=lambda s: _('In Progress'), translate=True, required=True)
    mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Email Template',
        domain=[('model', '=', 'project.task')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban')
    rating_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Rating Email Template',
        domain=[('model', '=', 'project.task')],
        help="If set and if the project's rating configuration is 'Rating when changing stage', "
             "then an email will be sent to the customer when the task reaches this step.")
    auto_validation_kanban_state = fields.Boolean('Automatic kanban status', default=False)
