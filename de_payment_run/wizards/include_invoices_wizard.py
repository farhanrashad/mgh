# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json

class IncludeInvoicesWizard(models.TransientModel):
    _name = 'account.payment.run.invoices.wizard'
    _description = 'Include Invoices through Wizard on Payment Run'

    
    payment_run_id = fields.Many2one(
        'account.payment.run', readonly=True, default=lambda self: self.env.context.get('active_id'))

    include_move_ids = fields.Many2many(
        'account.move',
        string='Invoices',
        store=True,
        domain=[('move_type', '!=', 'entry'), ('state', '=', 'posted'), ('amount_residual', '!=', 0)],
    )

    def action_process(self):
        for run in self.payment_run_id:
            run.include_move_ids = self.include_move_ids