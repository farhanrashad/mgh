# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError

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
       
        vals = {}
        vals = ({
            'name': self.name, 
            'purchase_id': self.id,
            #'analytic_account_id': False,
        })
        ms_project_id = self.env['project.project'].search([('purchase_id','=',self.id)],limit=1)
        if ms_project_id:
            ms_project_id.write({
                'active':True
            })
        else:
            ms_project_id = self.env['project.project'].sudo().create(vals)
        self.ms_project_id = ms_project_id.id
        self.ms_project_id.analytic_account_id.unlink()
        
        templates = self.env['purchase.task.template'].search([('order_type_id','=',self.order_type_id.id)])
        for stage in templates.stage_ids:
            stage.update({
                'project_ids': [(4, ms_project_id.id)]
            })
        
        stages_list = tasks_list = [] 
        stage_id = False
        for template in templates:
            task = ({
                'project_id': ms_project_id.id,
                #'purchase_project_id': project.id,
                'purchase_id': self.id,
                'name': ms_project_id.name + ' - ' + template.name,
                'partner_id': self.partner_id.id,
                'user_id': template.user_id.id,
                'date_deadline': fields.Date.to_string(self.date_approve + timedelta(template.completion_days)),
                'completion_days': template.completion_days,
                'approval_days': template.approval_days,
                'completion_percent': template.completion_percent,
                'task_sequence': template.sequence,
                'stage_id': stage_id,
                'purchase_task_stage_ids': [(6, 0, template.stage_ids.ids)],
                'purchase_task_template_id': template.id,
            })
            task_id = self.env['project.task'].sudo().create(task)
            task_id.update({
                'stage_id': task_id.purchase_task_stage_ids[0].id
            })
            for tdoc in template.template_doc_ids:
                docs = ({
                    'name': tdoc.name,
                    'task_id': task_id.id,
                })
                doc_id = self.env['project.task.documents'].sudo().create(docs)
                #compute stage of milestone tasks
            stages_list = []
            next_stage = prv_stage = False
            for stage in task_id.purchase_task_stage_ids:
                stages_list.append({
                    'task_id': task_id.id,
                    'stage_id': stage.id, 
                    'sequence': stage.sequence,
                })
            
            task_id.task_stage_ids.create(stages_list)
            #order.order_stage_ids = lines_data
            #===================================
            #++++++++Assign Next Stage++++++++++++++
            next_stages = self.env['project.task.stage'].search([('task_id','=', task_id.id)], order="sequence desc")
            for stage in next_stages:
                stage.update({
                    'next_stage_id': next_stage,
                })
                next_stage = stage.stage_id.id
            #++++++++++++++++++++++++++++++++++++++++
            #+++++++++++Assign Previous Stage++++++++++
            prv_stages = self.env['project.task.stage'].search([('task_id','=', task_id.id)], order="sequence asc")
            for stage in prv_stages:
                stage.update({
                    'prv_stage_id': prv_stage,
                })
                prv_stage = stage.stage_id.id
            
        #create task workflow
        tasks_list = []
        next_task = prv_task = False
        #if self.purchase_task_workflow_line:
            #self.purchase_task_workflow_line.unlink()
        #for project in projects:
        for task in self.task_ids:#.filtered(lambda p: p.purchase_project_id.id == project.id):
            tasks_list.append({
                'purchase_id': self.id,
                #'project_id': task.purchase_project_id.id,
                'task_id': task.id,
                'sequence': task.task_sequence,
            })
        self.purchase_task_workflow_line.create(tasks_list)
        #for project in projects:
        next_task = prv_task = False
        #++++++++Assign Next Stage++++++++++++++
        #for project in projects:
        next_task = prv_task = False
        tasks = self.env['purchase.task.workflow.line'].search([('purchase_id','=', self.id),], order="sequence desc")
        for ntask in tasks:
            ntask.update({
                'next_task_id': next_task,
            })
            next_task = ntask.task_id.id
        #+++++++++++Assign Previous Stage++++++++++
        tasks = self.env['purchase.task.workflow.line'].search([('purchase_id','=', self.id),], order="sequence asc")
        for ptask in tasks:
            ptask.update({
                'prv_task_id': prv_task,
            })
            prv_task = ptask.task_id.id
                
        return res

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