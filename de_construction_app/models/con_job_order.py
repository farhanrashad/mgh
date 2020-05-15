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
    _description = 'this is job order model'


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
            # 'view_type': 'form',
            # 'domain': [('opportunity_id', '=', self.id)],
            # 'context': dict(self._context, create=True, default_opportunity_id=self.id),
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
            # 'view_type': 'form',
            # 'domain': [('opportunity_id', '=', self.id)],
            # 'context': dict(self._context, create=True, default_opportunity_id=self.id),
        }

    def get_sub_task_count(self):
        count = self.env['con.projects'].search_count([])
        self.sub_task = count

    def get_notes_count(self):
        count = self.env['con.projects'].search_count([])
        self.notes_ad = count

    def _get_default_stage_id(self):
        """ Gives default stage_id """
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

    name = fields.Char()
    sub_task = fields.Integer(compute='get_sub_task_count')
    notes_ad = fields.Integer(compute='get_notes_count')
    active = fields.Boolean(string='Active', default=True)
    project_id = fields.Many2one('con.projects', string='Project')
    customer_name = fields.Many2one('res.partner', string='Customer')
    product_uom_quantity = fields.Integer(string='Quantity')
    product_uom = fields.Char(string='Unit Of Measure', default='Unit(s)')
    product_id = fields.Many2one(comodel_name="product.product", string="", required=False, )
    # product_id = fields.Char(string="", required=False, )
    assign_to = fields.Many2one('res.users', string='Assigned to')
    starting_date = fields.Date(strinng='Starting Date')
    ending_date = fields.Date(string='Ending Date')
    deadline = fields.Date(string='Deadline')
    tag_ids = fields.Many2many('res.company', string='Tags')
    material_planning_line = fields.One2many('material.planning.line', 'job_order_ref')
    stock_move_line = fields.One2many('stock.move.line', 'stock_move_ref')
    sub_task_line = fields.One2many('sub.tasks.line', 'sub_task_ref')
    time_sheet_line = fields.One2many('time.sheet.line', 'time_sheet')

    planned_hours = fields.Float(string="Planned Hours",  required=False, )
    planned_progres = fields.Integer(string="Progres", required=False, )
    material_requistion_line = fields.One2many(comodel_name="meterial.boq", inverse_name="picking_ids", string="", required=False, )
    note = fields.Html(string="Description" )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True, states={'draft': [('readonly', False)]})

    color = fields.Integer('Color Index', default=0)
    # priority = fields.Selection(string='Priority', index=True)
    # stage_id = fields.Many2one('crm.stage', string='Stage', ondelete='restrict', tracking=True, index=True, copy=False,
    #                            group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())
    kanban_state = fields.Selection(
        [('grey', 'No next activity planned'), ('red', 'Next activity late'), ('green', 'Next activity is planned')],
        string='Kanban State')

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
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', False)]


