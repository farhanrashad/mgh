# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
   
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    project_id = fields.Many2one('project.project', string='Project', store=True,readonly=True)
    task_id = fields.Many2one('project.task', string='Task', readonly=True, store=True, domain="['|',('project_id', '=', False),('project_id', '=', project_id)]")
    
    @api.onchange('task_id')
    def _onchange_task_id(self):
        if not self.task_id:
            return

        self = self.with_company(self.company_id)
        task = self.task_id
        
        self.project_id = task.project_id.id
        self.origin = task.name
        self.company_id = task.company_id.id
        self.picking_type_id = task.picking_type_id.id
        self.partner_id = task.project_id.partner_id.id
        self.location_dest_id = task.location_id.id
        self.scheduled_date = fields.Datetime.now()
        self.owner_id = task.project_id.partner_id.id
        name = self.name
        # Create requisition lines if necessary
        move_lines = []
        for line in task.project_task_material_line:
            # Create requisition line
            move_line_values = line._prepare_stock_move_line(name=name)
            move_lines.append((0, 0, move_line_values))
        self.move_ids_without_package = move_lines

    @api.depends('location_id','location_dest_id')
    def _get_project_all(self):
        for picking in self:
        #project_id = self.env['project.project'].search(['|',('location_id','=',self.location_id.id),('location_id','=',self.location_id.id)],limit=1)
            tasks = self.env['project.task'].search(['|',('location_id','=',picking.location_id.id),('location_id','=',picking.location_id.id)],limit=1)
            for task in tasks:
                picking.task_id = task.id
                picking.project_id = task.project_id.id
        if not self.task_id:
            self.task_id = False
            self.project_id = False
        #self.project_id = project_id.id