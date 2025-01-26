# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json

class BankAssignWizard(models.TransientModel):
    _name = 'account.bank.assign.wizard'
    _description = 'Bank Assignment Wizard'

    
    payment_run_line = fields.Many2many(
        'account.payment.run.line', default=lambda self: self.env.context.get('active_ids'))
    
    journal_id = fields.Many2one('account.journal', string='Journal', 
                                 domain="[('id','in',journal_ids_domain)]",
                                  store=True, readonly=False, required=True
                                 )

    journal_ids_domain = fields.Many2many('account.journal', string="Journal Domains",
                                          compute='_compute_journals',
                                         )

    @api.model
    def default_get(self, fields):
        res = super(BankAssignWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            res['payment_run_line'] = [(6, 0, active_ids)]
        return res
    
    @api.depends('payment_run_line')
    def _compute_journals(self):
        for record in self:
            companies = record.payment_run_line.mapped('company_id')
            if companies:
                journal_ids = self.env['account.journal'].search([
                    ('company_id', 'in', companies.ids),
                    ('type', 'in', ['cash', 'bank'])
                ])
                record.journal_ids_domain = journal_ids
            else:
                record.journal_ids_domain = self.env['account.journal']


    def action_assign(self):
        for line in self.payment_run_line:
            #if line.payment_run_id.state not in ('draft','proposal'):
            #    raise ValidationError("You cannot reassign bank to approved records.")
            line.write({
                'payment_journal_id': self.journal_id.id
            })
            

        
    