# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class HRJob(models.Model):
    _inherit = 'hr.job'
    
    advance_limit_method = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed amount')
        ], string='Advance Limit', default='percentage', required=True,)
    
    amount = fields.Float('Advance Amount', digits='Account', help="The percentage of amount to advance.")
    fixed_amount = fields.Monetary('Limit Amount (Fixed)', help="The fixed amount limit to advance.")
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.company.currency_id)
        
    @api.constrains('amount')
    def _check_amount_limit(self):
        for job in self:
            if job.advance_limit_method == 'percentage':
                if job.amount > 100 or job.amount <= 0: 
                    raise ValidationError(_("advance limit must be between 0 and 100."))


