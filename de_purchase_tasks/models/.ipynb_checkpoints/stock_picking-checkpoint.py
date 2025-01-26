# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
                
    def button_validate(self):
        if self.purchase_id:
            if any(line.stage_id.stage_category != 'close' for line in self.purchase_id.task_ids):
                raise UserError(_('One of the milestone is not completed.'))
            
        res = super(StockPicking, self).button_validate()
        
        return res
    
   