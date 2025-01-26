# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging  # Import logging module

_logger = logging.getLogger(__name__)  # Create a logger for this module


class PurchaseOrderType(models.Model):
    _name = 'purchase.order.type'
    _description = 'Purchase Order Type'
    
    name = fields.Char(string='Reference', copy=False, readonly=False, index=True,)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ms_project_id = fields.Many2one('project.project', string='Project', oldname="project_id", copy=False, domain="[('active','=',True)]")
    project_count = fields.Integer(string='Project counts', compute='_compute_project')
    task_ids = fields.One2many('project.task', 'purchase_id', string='Tasks', copy=False)
    task_count = fields.Integer(string='Task counts', compute='_compute_task_ids')
    
    order_type_id = fields.Many2one('purchase.order.type', string="Order Type", )

    purchase_task_workflow_line = fields.One2many('purchase.task.workflow.line', 'purchase_id', string='Task Workflow', copy=False)
    
    
    
    @api.depends('ms_project_id')
    def _compute_project(self):
        for order in self:
            order.project_count = len(order.ms_project_id)
    
    @api.depends('task_ids')
    def _compute_task_ids(self):
        for order in self:
            order.task_count = len(order.ms_project_id.task_ids)
            
            
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        self._create_project_and_tasks()

        for line in self.purchase_task_workflow_line:
            line.task_id._create_task_stages()
        return res

    def _create_project_and_tasks(self):
        """Creates a project and tasks based on the purchase order type's task templates and maintains workflow lines."""
        if not self.order_type_id:
            raise UserError(_('Please select an Order Type before confirming the purchase order.'))
    
        # Create a new project
        project_vals = {
            'name': f"{self.name} - Project",
            'active': False,
            'purchase_id': self.id,  # optional if you want to link the project to the purchase order
        }
        new_project = self.env['project.project'].create(project_vals)
    
        # Set the newly created project to the purchase order
        self.ms_project_id = new_project.id
    
        # Fetch task templates associated with the selected order type
        task_templates = self.env['purchase.task.template'].search([('order_type_id', '=', self.order_type_id.id)])
    
        previous_task = False  # Track the previous task
        for index, template in enumerate(task_templates):
            # Create task
            task_vals = {
                'name': template.name,
                'project_id': new_project.id,
                'purchase_id': self.id,
                'sequence': template.sequence,
                'stage_id': template.stage_ids[0].id if template.stage_ids else False,  # Take the first stage as default
                'user_id': template.user_id.id or self.env.user.id,  # Responsible user from template or current user
                'planned_hours': template.completion_days,  # You can use completion_days to set planned hours
            }
            new_task = self.env['project.task'].create(task_vals)
            _logger.info("Created task: %s", new_task)
    
            # Create workflow line and maintain sequence
            workflow_vals = {
                'purchase_id': self.id,
                'task_id': new_task.id,
                'sequence': index + 1,
                'prv_task_id': previous_task.id if previous_task else False,  # Set the previous task
            }
            workflow_line = self.env['purchase.task.workflow.line'].create(workflow_vals)
    
            # Link the previous task's `next_task_id` to this newly created task
            if previous_task:
                previous_workflow_line = self.env['purchase.task.workflow.line'].search([('task_id', '=', previous_task.id)])
                previous_workflow_line.write({'next_task_id': new_task.id})


            # Add the new project to all stages (stage_ids) in the task template
            if template.stage_ids:
                for stage in template.stage_ids:
                    # Update the stage with the new project
                    stage.write({'project_ids': [(4, new_project.id)]})  # Assuming project_ids is Many2many in project.task.type

            
            # Create associated task documents based on template or any other logic
            for doc in template.template_doc_ids:
                document_vals = {
                    'task_id': new_task.id,
                    'name': doc.name
                }
                self.env['project.task.documents'].create(document_vals)
        
            # Set this task as the previous task for the next iteration
            previous_task = new_task

    
        
    def reorder_tasks(self):
        """Reorders tasks based on their sequence and updates next/previous task relationships."""
        workflow_lines = self.env['purchase.task.workflow.line'].search([('purchase_id', '=', self.id)], order='sequence')
    
        previous_task = False
        for line in workflow_lines:
            # Update the previous task
            line.prv_task_id = previous_task.id if previous_task else False
    
            # Update the next task for the previous task
            if previous_task:
                previous_task.next_task_id = line.task_id.id
    
            # Set the current task as the previous task for the next iteration
            previous_task = line.task_id
    
        # The last task in the workflow should not have a next task
        if previous_task:
            previous_task.next_task_id = False

    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for order in self:
            order.purchase_task_workflow_line.unlink()
            order.ms_project_id.task_ids.unlink()
            order.ms_project_id.write({
                'active':False
            })
            #order.project_id.unlink()
        #    for tline in order.purchase_task_workflow_line:
        #        tline.unlink()
        #    
        #    order.purchase_task_workflow_line.unlink()
        #    order.project_id.unlink()
        return res
    
    def _compute_proj_count(self):
        for rec in self:
            self.project_count = self.env['project.project'].search_count([('project_id', '=', self.id)])

    def action_view_project(self):
        """
        To get Count against Project Task for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Project',
            'res_model': 'project.project',
            'domain': [('purchase_id', '=', self.id)],
            'context': {'create':False},
            'target': 'current',
            'view_mode': 'list,form',
        }

    def _compute_task_count(self):
        for rec in self:
            self.task_count = self.env['project.task'].search_count([('purchase_id', '=', self.id)])

    def action_view_tasks(self):
        """
        To get Count against Project Task for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Milestone',
            'res_model': 'project.task',
            'domain': [('purchase_id', '=', self.id)],
             'context': {'create':False},
            'target': 'current',
            'view_mode': 'list,form',
        }
    
class PurchaseTaskWorkflowLine(models.Model):
    _name = 'purchase.task.workflow.line'
    _description = 'Purchase task workflow line'
    _order = 'sequence'
    
    purchase_id = fields.Many2one('purchase.order', string='Purchase', index=True, required=True, ondelete='cascade')

    task_id = fields.Many2one('project.task', string='Task', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    sequence = fields.Integer(string='Sequence', readonly="1")
    next_task_id = fields.Many2one('project.task', string='Next Task', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    prv_task_id = fields.Many2one('project.task', string='Previous Task', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)