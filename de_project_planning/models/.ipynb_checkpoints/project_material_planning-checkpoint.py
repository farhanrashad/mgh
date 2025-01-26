# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class ProjectTaskMaterialPlanning(models.Model):
    _name = 'project.task.material.planning'
    _description = 'Material Planning'
    
    task_id = fields.Many2one('project.task', string='Task Reference', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain="[('purchase_ok', '=', True)]", change_default=True, ondelete='restrict') 
    product_template_id = fields.Many2one('product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('purchase_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    date_scheduled = fields.Date(string='Scheduled Date')


    @api.onchange('product_id')
    def product_id_change(self):
        self.product_uom = self.product_id.uom_id.id
        self.name = self.product_id.product_tmpl_id.name