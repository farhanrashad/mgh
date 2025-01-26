# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
   
class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    
    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade', index=True, copy=False)
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade', index=True, copy=False, domain="[('project_id', '=', project_id)]")
    
    @api.onchange('task_id')
    def _onchange_task_id(self):
        if not self.task_id:
            return

        self = self.with_company(self.company_id)
        task = self.task_id
        
        self.project_id = task.project_id.id
        self.origin = task.name
        self.company_id = task.company_id.id
        self.ordering_date = fields.Datetime.now()
        name = self.name
        # Create requisition lines if necessary
        requisition_lines = []
        for line in task.project_task_material_line:
            # Create requisition line
            requisition_line_values = line._prepare_purchase_requisition_line(name=name)
            requisition_lines.append((0, 0, requisition_line_values))
        self.line_ids = requisition_lines
