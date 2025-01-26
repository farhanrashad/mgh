# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectLocationWizard(models.TransientModel):
    _name = "stock.picking.project.location.wizard"
    _description = "Stock Picking Project Location Wizard"
        
    project_id = fields.Many2one('project.project', string='Project', domain=[('allow_site_planning', '=', True)],)
    task_id = fields.Many2one('project.task', string='Job Order')
    assign_owner = fields.Boolean(string='Assign Owner')
    partner_id = fields.Many2one('res.partner', string='Partner', related='project_id.partner_id')
    location_id = fields.Many2one('stock.location', string='Location', related='project_id.location_id')
    
        
    @api.model
    def default_get(self,  default_fields):
        res = super(ProjectLocationWizard, self).default_get(default_fields)
        picking_id = self.env['stock.picking'].browse(self._context.get('active_ids',[]))
        
        res.update({
            #'product_id': entry_id.custom_entry_type_id.dp_product_id.id,
        })  
        return res
    
    def update_project_location(self):
        amount = 0
        picking_id = self.env['stock.picking'].browse(self._context.get('active_ids', []))
        location_id = picking_id.location_id.id
        location_dest_id = picking_id.location_dest_id.id
        owner_id = False
        if picking_id.picking_type_code == 'outgoing':
            location_id = self.location_id.id
        else:
            location_dest_id = self.location_id.id
        
        if self.assign_owner:
            owner_id = self.partner_id.id
            
        picking_id.update({
            'project_id': self.project_id.id,
            'task_id': self.task_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'owner_id': owner_id,
        })
        
        for move in picking_id.move_ids_without_package:
            move.update({
                'project_id': self.project_id.id,
                'task_id': self.task_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            })
            for ml in move.move_line_ids:
                ml.update({
                    'project_id': self.project_id.id,
                    'task_id': self.task_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'owner_id': owner_id,
                })