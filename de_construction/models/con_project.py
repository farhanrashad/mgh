# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class ConProjects(models.Model):
    _name = 'con.projects'
    _description = 'Construction Project'
    _rec_name = 'project_name'

    def _compute_task_count(self):
        task_data = self.env['job.order'].read_group(
            [('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)],
            ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.task_count = result.get(project.id, 0)

    def get_document_count(self):
        count = self.env['con.projects'].search_count([])
        self.documents_count = count

    def get_task_count(self):
        for rec in self:
            count = self.env['job.order'].search_count([('project_id', '=', rec.id)])
            rec.task_count = count

    def get_notes_count(self):
        for rec in self:
            count = self.env['project.notes'].search_count([('project_id', '=', rec.id)])
            rec.notes_count = count

    def _compute_favorite_ok(self):
        for project in self:
            project.favorite_ok = self.env.user in project.favorite_user_ids

    def _inverse_favorite_ok(self):
        favorite_projects = not_fav_projects = self.env['con.projects'].sudo()
        for project in self:
            if self.env.user in project.favorite_user_ids:
                favorite_projects |= project
            else:
                not_fav_projects |= project
        # Project User has no write access for project.
        not_fav_projects.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_projects.write({'favorite_user_ids': [(3, self.env.uid)]})

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    @api.model
    def activate_sample_project(self):
        """ Unarchives the sample project 'project.project_project_data' and
            reloads the project dashboard """
        # Unarchive sample project
        project = self.env.ref('de_construction.projects_projects_data', False)
        if project:
            project.write({'active': True})

        cover_image = self.env.ref('de_construction.msg_task_data_14_attach', False)
        cover_task = self.env.ref('de_construction.order_job_data_14', False)
        if cover_image and cover_task:
            cover_task.write({'displayed_image_id': cover_image.id})

        # Change the help message on the action (no more activate project)
        action = self.env.ref('de_construction.open_view_project_all', False)
        action_data = None
        if action:
            action.sudo().write({
                "help": _('''<p class="o_view_nocontent_smiling_face">
                          Create a new project</p>''')
            })
            action_data = action.read()[0]
        # Reload the dashboard
        return action_data

    def open_tasks(self):
        ctx = dict(self._context)
        ctx.update({'search_default_project_id': self.id})
        action = self.env['ir.actions.act_window'].for_xml_id('de_construction',
                                                              'act_project_project_2_project_task_all')
        return dict(action, context=ctx)

    def con_task_button(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'multi': False,
            'name': 'Tasks',
            'domain': [('project_id', '=', self.id)],
            'target': 'current',
            'res_model': 'job.order',
            'view_mode': 'kanban,form',
        }

    def notes_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'multi': False,
            'name': 'Tasks',
            'domain': [('project_id', '=', self.id)],
            'target': 'current',
            'res_model': 'project.notes',
            'view_mode': 'tree,form',
        }

    # @api.depends('visibility')
    # def set_default_value(self):
    #     for i in self:
    #         i.visibility = 'All employees'

    rating_status = fields.Selection(
        [('stage', 'Rating when changing stage'),
         ('periodic', 'Periodical Rating'),
         ('no', 'No rating')],
        string='Customer(s) Ratings', default='no', required=True)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account',
                                          copy=False)
    favorite_ok = fields.Boolean(compute='_compute_favorite_ok', inverse='_inverse_favorite_ok',
                                 string='Show Project on dashboard',
    alias_id = fields.Many2one(comodel_name='mail.alias', string='Alias', ondelete='restrict',
                               required=True))
    task_id = fields.Char(string='Use Tasks as', default='Tasks')
    project_name = fields.Char(string='Name', bold=True, required=True)
    task_name = fields.Char(string='Name of the tasks:')
    documents_count = fields.Integer(compute='get_document_count')
    task_count = fields.Integer(compute='get_task_count')
    notes_count = fields.Integer(compute='get_notes_count')
    manager_id = fields.Many2one(comodel_name='res.users', string='Project Manager')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', auto_join=True, tracking=True)
    user_id = fields.Many2one(comodel_name='res.users', string='User', default=lambda self: self.env.user,
                              tracking=True)
    image_hr = fields.Binary(string='image')
    visibility = fields.Selection([('invited_employee', 'Invited employee'),
                                   ('all_employee', 'All Employee'),
                                   ('portal_user', 'Portal user')],
                                  string='Visibility')
    sub_task_project = fields.Many2one(comodel_name='con.projects', string='Sub-task Project')
    company_id = fields.Many2one(comodel_name='res.company', string='Company')
    time_sheet = fields.Boolean(string='Time  Sheets', store=True)
    customer_rating = fields.Selection([('changing_stage', 'Rating When changing stage'),
                                        ('all_employee', 'Periodically Rating'),
                                        ('portal_user', 'No rating')],
                                       string='Customer Ratings')
    site_id = fields.Selection([('agriculture', 'Agriculture'),
                                ('residential', 'Residential'),
                                ('commercial', 'Commercial')],
                               string='Type of Construction')
    location_id = fields.Many2one(comodel_name='res.partner', string='Location')
    active = fields.Boolean(default=True)
    displayed_image_id = fields.Many2one(comodel_name='ir.attachment',
                                         domain="[('res_model', '=', 'job.order'), "
                                                "('res_id', '=', id), ('mimetype', 'ilike', 'image')]",
                                         string='Cover Image')
    color = fields.Integer(string='Color Index')
    working_time = fields.Many2one(comodel_name='resource.calendar', string='Working Time')
