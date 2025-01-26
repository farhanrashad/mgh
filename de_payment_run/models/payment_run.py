# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import safe_eval
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)

STATES = [
    ('draft', 'Draft'), 
    ('proposal', 'Proposal'),
    ('submit', 'Submitted'),
    ('scheduled', 'Scheduled'),
    ('approve', 'Approved'),
    ('posted', 'Posted'),
    ('cancel', 'Cancel'),  
]

class PaymentRun(models.Model):
    _name = 'account.payment.run'
    _description = "Payment Run"
    _order = "date desc, name desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _sequence_index = "journal_id"

    name = fields.Char(
        string='Reference',
        copy=False,
        tracking=True,
        index='trigram',
    )

    run_method = fields.Selection([
        ('now', 'Now'),
        ('scheduled', 'Schedule Later'),
    ], string='When', default='now', required=True,
    )
    
    date = fields.Date(
        string='Run Date',
        index=True,
        store=True, required=True, readonly=False,
        default=lambda self: fields.Date.context_today(self),
        copy=False,
        tracking=True,
        compute='_compute_run_date'
    )

    date_next_run = fields.Date(
        string='Next Run Date',
        index=True,
        store=True, required=True, readonly=False,
        default=lambda self: (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        copy=False,
    )
    
    state = fields.Selection(
        selection=STATES,
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
        store=True,
        compute='_compute_state'
    )
    
    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True, tracking=True)
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], default='customer', tracking=True, required=True)
    
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    exclude_partner_ids = fields.Many2many(
        'res.partner',
        'partner_payment_run_rel',
        'partner_id',
        'payment_run_id',
        string='Excluded Partners'
    )
    include_move_ids = fields.Many2many(
        'account.move',
        'account_move_payment_run_rel',
        'move_id',
        'payment_run_id',
        string='Invoices',
        store=True,
        #compute='_compute_include_move_ids',
    )

    # New computed field with only the move_id included
    include_move_ids_domain = fields.Many2many(
        'account.move',
        string='Filtered Invoices',
        compute='_compute_include_move_ids_domain',
    )            

    group_payment = fields.Boolean(string='Group Payment',
                                    help='combine partner multiple payments in one payment.',
                                  )

    # Parameter fields
    date_invoice = fields.Date(
        string='Invoice Date Up To',
        copy=False,
    )
    date_accounting = fields.Date(
        string='Accounting Date',
        copy=False,
    )
    date_due_by = fields.Date(
        string='Items Due By',
        copy=False,
    )
    # Extra Selection
    filter_domain = fields.Char(string='Apply On', help="If present, this domain would apply to filter accounting documents.")

    # to pay accounting documents
    line_ids = fields.One2many(
        'account.payment.run.line',
        'payment_run_id',
        string='Propose Accounting Documents',
        copy=True,
    )
    count_proposal = fields.Integer('Proposals',
                                    compute='_compute_proposal_count',
                                   )
    count_payments = fields.Integer('Payments',
                                    compute='_compute_payment_count',
                                   )
    
    # Computed Methods(self)
    @api.depends('run_method')
    def _compute_run_date(self):
        for record in self:
            if record.run_method == 'now':
                record.date = fields.Date.today()

    @api.depends('line_ids')
    def _compute_proposal_count(self):
        for proposal in self:
            proposal.count_proposal = len(self.line_ids)

    def _compute_payment_count(self):
        for proposal in self:
            proposal.count_payments = len(proposal.line_ids.mapped('payment_id'))


    
    def _compute_include_move_ids_domain(self):
        for record in self:
                record.include_move_ids_domain = self.env['account.move'].search([
                    ('move_type', '!=', 'entry'),
                    ('state', '=', 'posted'),
                    ('amount_residual', '!=', 0),
                ])

    #@api.depends('line_ids')
    #def _compute_include_move_ids(self):
    #    for record in self:
    #        if record.state == 'submit':
    #           record.include_move_ids = self.env['account.move'].search([
    #                ('id', 'in', self.line_ids.mapped('move_id').ids)
    #            ])
    #        else:
    #            record.include_move_ids.unlink()

    
    # CRUD Methods
    
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError("You can only delete records in draft state.")
        return super(PaymentRun, self).unlink()

    # Actions
    def button_prepare_proposal(self):
        domain = self._prepare_domain()

        move_ids = self.env['account.move'].search(domain)
        self.line_ids.unlink()
        for move in move_ids:
            self.env['account.payment.run.line'].create(self._prepare_payment_run_line(move))
            self.write({
                'state': 'proposal',
            })
        self.state = 'proposal'

    def button_select_invoices(self):
        active_id = self.env.context.get('active_id') or self.id
        return {
            'name': 'Select Invoices',
            'view_mode': 'form',
            'res_model': 'account.payment.run.invoices.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'active_id': active_id}
        }
        
    def button_draft(self):
        self.line_ids.unlink()
        self.write({
            'state': 'draft',
        })

    def button_schedule(self):
        self.write({
            'state': 'scheduled',
        })

    def button_approve(self):
         self.write({
                'state': 'approve',
            })

    def button_cancel(self):
        self.write({
            'state': 'cancel',
        })
        self.line_ids.unlink()

    def button_submit(self):
        self.write({
            'state': 'submit',
        })
        self.line_ids.write({
            'state': 'submit',
        })
    def button_post(self):
        if not self.date_accounting:
            raise UserError('Accounting Date is required')
            
        if self.group_payment:
            self._create_payment(self.group_payment)
        else:
            self._create_multiple_payments()

        if self.run_method == 'scheduled':
            if self.date == fields.Date.today():
                raise UserError('Run date must be in future')
            self.write({
                'state': 'scheduled',
            })
        else:
            self.write({
                'state': 'posted',
            })
            

    @api.model
    def _cron_execute_scheduled(self):
        """ Method called by the cron job that searches for account.payment.run that were scheduled and need
        to be executed and calls _action_post() on them."""

        payment_run_ids = self.search([
            ('run_method', '=', 'scheduled'),
            ('state', '=', 'scheduled'),
            ('date', '<=', fields.Datetime.now())
        ])
        for payment in payment_run_ids:
            if payment.grpup_payment:
                payment._create_payment(payment.group_payment)
            else:
                payment._create_multiple_payments()

    
    def _create_payment(self, group_payment=False):
        if group_payment:
            partner_lines = defaultdict(list)
            for move in self.line_ids.filtered(lambda x:x.state == 'approve'):
                partner_lines[move.move_id.partner_id.id].append(move)
            for partner_id, lines in partner_lines.items():
                total_amount = sum(line.amount_to_pay for line in lines)
                payment_vals = self._prepare_payment(lines[0])
                payment_vals.update({
                    'amount': abs(total_amount),
                    'payment_run_id': self.id,
                })
                payment_id = self.env['account.payment'].create(payment_vals)
                payment_id.action_post()
                for line in lines:
                    line.write({'payment_id': payment_id.id})
                    line._reconcile_payment(line.move_id, payment_id.move_id)

    def _create_multiple_payments(self):
        for move in self.line_ids.filtered(lambda x:x.state == 'approve'):
            payment_vals = self._prepare_payment(move)
            payment_vals.update({
                'amount': abs(move.amount_to_pay),
                'payment_run_id': self.id,
            })
            payment_id = self.env['account.payment'].create(payment_vals)
            payment_id.action_post()
            move.write({'payment_id': payment_id.id})
            move._reconcile_payment(move.move_id, payment_id.move_id)
            
    def _prepare_payment(self,line):
        vals = {
            'partner_type': self.partner_type,
            'partner_id': line.partner_id.id,
            'date': self.date_accounting,
            'ref': line.move_id.name,
            'journal_id': line.payment_journal_id.id or self.company_id.pr_default_journal_id.id,
            'amount': abs(line.amount_to_pay),
            'payment_run_id': self.id,
        }
        if line.move_id.move_type == 'in_refund' or line.move_id.move_type == 'out_invoice':
            vals['payment_type'] = 'inbound'
        else:
            vals['payment_type'] = 'outbound'
            
        return vals

    

    def _prepare_payment_run_line(self,move):
        return {
            'payment_run_id': self.id,
            'move_id': move.id,
            'state':'proposal',
            'payment_journal_id': move.partner_id.pr_journal_id.id or self.company_id.pr_default_journal_id.id
        }
    

    def _prepare_domain(self):
        # Base domain: applies to all records
        base_domain = [
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', self.company_id.id),
            ('partner_id', 'not in', self.exclude_partner_ids.ids),
            ('move_type', '!=', 'entry'),
            ('state', '=', 'posted'),
            ('amount_residual', '!=', 0),
        ]
        
        # Payment type domain: filters by inbound/outbound payment type
        if self.payment_type == 'inbound':
            payment_type_domain = [('move_type', 'in', ('out_invoice', 'in_refund'))]
        elif self.payment_type == 'outbound':
            payment_type_domain = [('move_type', 'in', ('in_invoice', 'out_refund'))]
        else:
            payment_type_domain = []
    
        # Invoice date domain: filters by invoice date
        invoice_date_domain = [('invoice_date', '<=', self.date_invoice)] if self.date_invoice else []
    
        # Due date domain: filters by due date
        due_date_domain = [('invoice_date_due', '<=', self.date_due_by)] if self.date_due_by else []
    
        # Include only selected move IDs (if any)
        if self.include_move_ids:
            include_moves_domain = [('id', 'in', self.include_move_ids.ids)]
        else:
            include_moves_domain = []
    
        # Additional filters from filter_domain (evaluated dynamically)
        try:
            custom_filter_domain = safe_eval(self.filter_domain) if self.filter_domain else []
        except Exception as e:
            _logger.error("Failed to evaluate filter domain: %s", e)
            custom_filter_domain = []
    
        # Combine all domains using AND logic
        final_domain = expression.AND([
            base_domain,
            payment_type_domain,
            invoice_date_domain,
            due_date_domain,
            include_moves_domain,
            custom_filter_domain,
        ])
    
        _logger.info("Generated Search Domain: %s", final_domain)
        return final_domain



        
        
    def open_payment_proposal(self):
        # Fetch the action for displaying payment run lines
        action = self.env.ref('de_payment_run.action_payment_run_line_display').read()[0]
        
        # Initialize the context and flags
        edit_flag = False
        delete_flag = False
    
        # Check if the current state allows editing and deletion
        if self.state in ['draft', 'proposal']:
            edit_flag = True
            delete_flag = True
    
        # Update the action dictionary with the proper configurations
        action.update({
            'name': 'Accounting Documents',
            'view_mode': 'list',
            'res_model': 'account.payment.run.line',
            'type': 'ir.actions.act_window',
            'domain': [('payment_run_id', '=', self.id)],
            'context': {
                'create': False,
                'edit': edit_flag,  # Allow editing if state is 'draft' or 'proposal'
                'delete': delete_flag,  # Allow deletion if state is 'draft' or 'proposal'
            },
            'flags': {
                'action_buttons': True,
                'delete': delete_flag,  # Handle delete permissions based on the state
                'readonly': not edit_flag  # Set the readonly mode based on the state
            }
        })
    
        return action


    def open_payments(self):
        if self.partner_type == 'supplier':
            action = self.env.ref('account.action_account_payments_payable').read()[0]
        else:
            action = self.env.ref('account.action_account_payments').read()[0]
            
        action.update({
            'name': 'Payment',
            'view_mode': 'list',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('payment_run_id','=',self.id),('state','!=','cancel')],
            'context': {
                'create': False,
                'edit': True,
            },
            
        })
        return action

    @api.depends('line_ids.state')
    def _compute_state(self):
        for record in self:
            if record.line_ids:
                # Check if all line items are either approved or rejected
                if all(line.state in ['approve', 'cancel'] for line in record.line_ids):
                    record.state = 'approve'
        
    


class PaymentRunLine(models.Model):
    _name = "account.payment.run.line"
    _description = "Payment Run Items"

    payment_run_id = fields.Many2one(
        comodel_name='account.payment.run',
        string='Payment Run',
        required=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
        check_company=True,
    )
    company_id = fields.Many2one(
        related='payment_run_id.company_id', store=True, readonly=True, precompute=True,
        index=True,
    )
    #currency_id = fields.Many2one(
    #    related='payment_run_id.currency_id', store=True, readonly=True, precompute=True,
    #    index=True,
    #)
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        required=True,
        readonly=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
        check_company=True,
    )
    partner_id = fields.Many2one(related='move_id.partner_id')
    payment_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Journal",
        check_company=True,
        domain="[('type', 'in', ('bank','cash'))]",
    )
    currency_id = fields.Many2one('res.currency', 
                                          compute='_compute_payment_journal_currency',
                                          store=True, 
                                         )
    invoice_date = fields.Date(related='move_id.invoice_date')
    invoice_date_due = fields.Date(related='move_id.invoice_date_due')
    
    amount_total_signed = fields.Monetary(related='move_id.amount_total_signed')
    amount_residual_signed = fields.Monetary(related='move_id.amount_residual_signed')
    amount_total = fields.Monetary(related='move_id.amount_total')
    amount_residual = fields.Monetary(related='move_id.amount_residual')
    #currency_id = fields.Many2one(related='move_id.currency_id' )
    
    amount_to_pay = fields.Monetary(
        string='Amount to Pay',
        store=True,
        readonly=False,
        compute='_compute_to_pay_amount',
    )
    exclude_for_payment = fields.Boolean('Exclude')
    parent_state = fields.Char('payment_run_id.state')

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string="Payment",
        readonly=True,
        compute='_compute_payment',
        domain="[('state','!=','cancel')]",
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proposal', 'Proposal'),
        ('submit','Submitted'),
        ('approve', 'Approved'),
        ('posted', 'Posted'),
        ('cancel', 'Cancel'),  
    ], default='draft', store=True, readonly=False,
                
                             required=True)

    @api.depends(
        'payment_run_id',
        'payment_run_id.state',
                )
    def _compute_state(self):
        for record in self:
            if record.payment_run_id.state not in ('approve'):
                record.state = record.payment_run_id.state
            
    @api.depends('move_id','payment_journal_id')
    def _compute_payment_journal_currency(self):
        for record in self:
            if record.payment_journal_id.currency_id:
                record.currency_id = record.payment_journal_id.currency_id
            else:
                record.currency_id = record.move_id.currency_id
                
                
    @api.depends('payment_id.state')
    def _compute_payment(self):
        for record in self:
            if record.payment_id.state == 'cancel':
                record.payment_id = False
        
    @api.depends('move_id')
    def _compute_to_pay_amount(self):
        for record in self:
            record.amount_to_pay = record.move_id.amount_residual_signed

    def open_Journal_entry(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action.update({
            'name': 'Accounting Documents',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('id','=',self.move_id.id)],
            'context': {
                'create': False,
                'edit': False,
                'active_id': self.move_id.id,  
                'active_model': 'account.move',
            },
            
        })
        return action
        
    def _reconcile_payment(self, move_id, payment_move_id):
        move_lines = move_id.line_ids.filtered(
            lambda line: line.account_id.id in self._find_accounts(line) and line.account_id.reconcile
        )
        payment_lines = payment_move_id.line_ids.filtered(
            lambda line: line.account_id.id in self._find_accounts(line) and line.account_id.reconcile
        )
        (move_lines + payment_lines).reconcile()
    
    def _find_accounts(self, line):
        payable_account_id = line.partner_id.property_account_payable_id.id
        receivable_account_id = line.partner_id.property_account_receivable_id.id
        
        return [
            payable_account_id,
            receivable_account_id,
        ] if payable_account_id and receivable_account_id else []



    def action_bank_assignment(self):
        active_ids = self.env.context.get('active_ids')
        return {
            'name': 'Assign Bank',
            'view_mode': 'form',
            'res_model': 'account.bank.assign.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'active_ids': active_ids}
        }

    def action_approve(self):
        for record in self:
            if record.payment_run_id.state not in ('submit'):
                raise UserError('You cannot approve the posted or cancelled document')
            record.state = 'approve'

    def action_reject(self):
        for record in self:
            if record.payment_run_id.state not in ('submit'):
                raise UserError('You cannot reject the posted or cancelled document')
            record.state = 'cancel'
            record.amount_to_pay = 0

    def unlink(self):
        # Capture the move_ids to be removed from line_ids before deletion
        move_ids_to_remove = self.mapped('move_id')

        # Store the reference to the related payment_run_id before the unlink happens
        payment_run_records = self.mapped('payment_run_id')

        # Proceed with the unlink (delete)
        result = super(PaymentRunLine, self).unlink()

        # Now remove the corresponding move_ids from include_move_ids in the parent model
        for payment_run in payment_run_records:
            payment_run.write({
                'include_move_ids': [(3, move_id.id, 0) for move_id in move_ids_to_remove]
            })

        return result
