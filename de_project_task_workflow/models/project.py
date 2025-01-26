# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
from datetime import timedelta, datetime
from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from odoo.tools.misc import format_date, get_lang
from odoo.osv.expression import OR

import logging  # Import logging module

_logger = logging.getLogger(__name__)  # Create a logger for this module


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    stage_id = fields.Many2one('project.task.type', 'Parent Stage', index=True, ondelete='cascade')
    #complete_name = fields.Char("Full Stage Name", compute='_compute_complete_name', store=True)
    stage_code = fields.Char(string='Code', size=3)
    
    stage_category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('close', 'Closed'),
    ], string='Category', default='draft')
    
    group_id = fields.Many2one('res.groups', string='Security Group')
    
    @api.depends('name', 'stage_id.complete_name')
    def _compute_complete_name(self):
        for stage in self:
            if stage.stage_id:
                stage.complete_name = '%s/%s' % (stage.stage_id.complete_name, stage.name)
            else:
                stage.complete_name = stage.name    

class ProjectProejct(models.Model):
    _inherit = 'project.project'
    
    project_stage_ids = fields.One2many('project.stage', 'project_id', string='Project Stage', copy=True)
    
class ProjectStage(models.Model):
    _name = 'project.stage'
    _description = 'Project Task Stages'
    _order = 'sequence'
    
    project_id = fields.Many2one('project.task', string='Task', index=True, required=True, ondelete='cascade')
    stage_id = fields.Many2one('project.task.type', string='Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    sequence = fields.Integer(string='Sequence')
    next_stage_id = fields.Many2one('project.task.type', string='Next Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    prv_stage_id = fields.Many2one('project.task.type', string='Previous Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    
class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    task_stage_ids = fields.One2many('project.task.stage', 'task_id', string='Stage', copy=True)
    
    next_stage_id = fields.Many2one('project.task.type', string='Next Stage', compute='_compute_task_stage')
    prv_stage_id = fields.Many2one('project.task.type', string='Previous Stage', compute='_compute_task_stage')
    stage_code = fields.Char(related='stage_id.stage_code')
    stage_category = fields.Selection(related='stage_id.stage_category')
    date_submit = fields.Datetime('Submission Date', readonly=False)
    date_approved = fields.Datetime('Approved Date', readonly=False)
    date_refused = fields.Datetime('Refused Date', readonly=False)

    
        
    def write(self, vals):
        stage_id = self.env['project.task.type']
        result = super(ProjectTask,self).write(vals)
         # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            stage_id = self.env['project.task.type'].browse(vals.get('stage_id'))
            for task in self.sudo():
                group_id = stage_id.group_id
                if group_id:
                    if not (group_id & self.env.user.groups_id):
                        raise UserError(_("You are not authorize to approve '%s'.", stage_id.name))

        # Ensure stages are created after project_id is set
        #if not self.task_stage_ids:
        #    self._create_task_stages()
        return result

    def create1(self, vals):
        # Create the task first
        task = super(ProjectTask, self).create(vals)
        
        # Check if the project_id exists in the creation values
        if 'project_id' in vals:
            # Call the method to create and link the stages
            if not self.task_stage_ids:
                task._create_task_stages()
        return task

    @api.onchange('project_id')
    def _project_id_onchange(self):
        if not self.task_stage_ids:
            self._create_task_stages()
            
    def _compute_task_stage(self):
        for task in self:
            next_stage = prv_stage = False
            for stage in task.task_stage_ids.filtered(lambda t: t.stage_id.id == task.stage_id.id):
                    next_stage = stage.next_stage_id.id
                    prv_stage = stage.prv_stage_id.id
            task.next_stage_id = next_stage
            task.prv_stage_id = prv_stage
            
    def action_submit(self):
        for task in self.sudo():
            group_id = task.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to submit task."))
        self.update({
            'stage_id' : self.next_stage_id.id,
            'date_submit' : fields.Datetime.now(),
        })
        
    def action_confirm(self):
        for task in self.sudo():
            group_id = task.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to approve '%s'.", task.stage_id.name))
        
        if not self.next_stage_id:
            raise UserError(_("No stage to move forward."))
            
        self.update({
            'date_approved' : fields.Datetime.now(),
            'stage_id' : self.next_stage_id.id,
        })
        
    def action_refuse(self):
        for task in self.sudo():
            group_id = task.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to approve '%s'.", task.stage_id.name))
        
        if not self.prv_stage_id:
            raise UserError(_("No stage to move backward."))
            
        self.update({
            'date_refused' : fields.Datetime.now(),
            'stage_id' : self.prv_stage_id.id,
        })

    
    def _create_task_stages(self):
        project_stages = self.env['project.task.type'].search([('project_ids', 'in', self.project_id.id)], order='sequence')
    
        previous_stage = None  # Initialize as None
    
        for stage in project_stages:
            # Create task stage
            next_stage = self.env['project.task.type'].search([('project_ids', 'in', self.project_id.id),('sequence','>', stage.sequence)], limit=1)
            prv_stage = self.env['project.task.type'].search([('project_ids', 'in', self.project_id.id),('sequence','<', stage.sequence)], limit=1, order='sequence desc')


            vals = {
                'task_id': self.id,
                'stage_id': stage.id,
                'sequence': stage.sequence,
                'next_stage_id': next_stage.id,
                'prv_stage_id': prv_stage.id,
            }
            task_stage = self.env['project.task.stage'].create(vals)

            _logger.info("Created task: %s (ID: %s)", self.id, task_stage.stage_id.name)
    
            #if previous_stage:
            #    previous_stage.next_stage_id = task_stage.id  # Set next_stage_id to the current task_stage
    
            #previous_stage = task_stage


class ProjectTaskStage(models.Model):
    _name = 'project.task.stage'
    _description = 'Project Task Stages'
    _order = 'sequence'
    
    task_id = fields.Many2one('project.task', string='Task', index=True, required=True, ondelete='cascade')

    stage_id = fields.Many2one('project.task.type', string='Stage', readonly=False, )
    sequence = fields.Integer(string='Sequence')
    next_stage_id = fields.Many2one('project.task.type', string='Next Stage', readonly=False, )
    prv_stage_id = fields.Many2one('project.task.type', string='Previous Stage', readonly=False, )
    
    