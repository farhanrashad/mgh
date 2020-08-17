# -*- coding: utf-8 -*-
import logging
from psycopg2 import sql, extras
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
from odoo.addons.phone_validation.tools import phone_validation
from collections import OrderedDict


class JobOrder(models.Model):
    _name = 'job.order'
    _description = 'Job Order'
    _rec_name = 'name'

    def con_job_order_notes_button(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'multi': False,
            'name': 'Tasks',
            'target': 'current',
            'res_model': 'job.notes',
            'view_mode': 'kanban,form',
        }

    def con_sub_tasks_smart_button(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'multi': False,
            'name': 'Tasks',
            'target': 'current',
            'res_model': 'job.order',
            'view_mode': 'kanban,form',
        }

    def get_sub_task_count(self):
        count = self.env['con.projects'].search_count([])
        self.sub_task = count

    def get_notes_count(self):
        count = self.env['con.projects'].search_count([])
        self.notes_ad = count

    def _get_default_stage_id(self):
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _compute_kanban_state(self):
        today = date.today()
        for lead in self:
            kanban_state = 'grey'
            if lead.activity_date_deadline:
                lead_date = fields.Date.from_string(lead.activity_date_deadline)
                if lead_date >= today:
                    kanban_state = 'green'
                else:
                    kanban_state = 'red'
            lead.kanban_state = kanban_state

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', False)]

    def _compute_planned_hours(self):
        total = 0.0
        for line in self.time_sheet_line:
            total = total + line.time_period
        self.planned_hours = total

    def _get_planned_hours_progress(self):
        self.planned_progress = self.planned_hours

    def action_sub_task_creation(self):
        wizard_view_id = self.env.ref(
            'de_construction.con_job_order_form')
        return {
            'name': _('Sub Task'),
            'res_model': 'job.order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_view_id.id,
            'target': 'new',
        }

    name = fields.Char(required=True)
    sub_task = fields.Integer(string='Sub Task', compute='get_sub_task_count')
    notes_ad = fields.Integer(string='Notes', compute='get_notes_count')
    active = fields.Boolean(string='Active', default=True)
    project_id = fields.Many2one(comodel_name='con.projects', string='Project')
    customer_name = fields.Many2one(comodel_name='res.partner', string='Customer')
    product_uom_quantity = fields.Integer(string='Quantity')
    product_uom = fields.Many2one(comodel_name='uom.uom', string='Unit Of Measure')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    assign_to = fields.Many2one(comodel_name='res.users', string='Assigned to')
    starting_date = fields.Date(strinng='Starting Date')
    ending_date = fields.Date(string='Ending Date')
    deadline = fields.Date(string='Deadline')
    tag_ids = fields.Many2many(comodel_name='res.company', string='Tags')
    material_planning_line = fields.One2many(comodel_name='material.planning.line', inverse_name='job_order_ref')
    stock_move_line = fields.One2many(comodel_name='stock.move.line', inverse_name='stock_move_ref')
    sub_task_line = fields.One2many(comodel_name='sub.tasks.line', inverse_name='sub_task_ref')
    time_sheet_line = fields.One2many(comodel_name='time.sheet.line', inverse_name='time_sheet')
    planned_hours = fields.Float(string='Planned Hours', compute='_compute_planned_hours')
    planned_progress = fields.Integer(string='Progress', widget="progressbar",
                                      compute='_get_planned_hours_progress')
    max_rate = fields.Integer(string='Maximum rate', default=100)
    material_requisition_line = fields.One2many(comodel_name='material.boq', inverse_name='picking_ids')
    note = fields.Html(string='Description')
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account',
                                          readonly=True, states={'draft': [('readonly', False)]})
    color = fields.Integer('Color Index', default=0)
    # priority = fields.Selection(string='Priority', index=True)
    kanban_state = fields.Selection(
        [('grey', 'No next activity planned'),
         ('red', 'Next activity late'),
         ('green', 'Next activity is planned')],
        string='Kanban State')
