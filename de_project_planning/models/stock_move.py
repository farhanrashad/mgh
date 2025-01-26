# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
   
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    task_id = fields.Many2one('project.task', compute='_get_project_all', store=True, readonly=False )
    project_id = fields.Many2one('project.project', compute='_get_project_all', store=True, readonly=False)
    #component_task_id = fields.Many2one('project.task', 'Task for consumed products', index=True)
    
    @api.depends('picking_id')
    def _get_project_all(self):
        project_id = self.env['project.project']
        task_id = self.env['project.task']
        for move in self:
            if move.picking_id:
                for picking in move.picking_id:
                    project_id = picking.project_id
                    task_id = picking.task_id
            move.task_id = task_id.id
            move.project_id = project_id.id
                
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    task_id = fields.Many2one('project.task', compute='_get_project_all', store=True, readonly=False )
    project_id = fields.Many2one('project.project', compute='_get_project_all', store=True, readonly=False)
    #component_task_id = fields.Many2one('project.task', 'Task for consumed products', index=True)
    
    @api.depends('picking_id')
    def _get_project_all(self):
        project_id = self.env['project.project']
        task_id = self.env['project.task']
        for move in self:
            if move.picking_id.id:
                for picking in move.picking_id:
                    project_id = picking.project_id
                    task_id = picking.task_id
            move.task_id = task_id.id
            move.project_id = project_id.id

