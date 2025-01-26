# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"
    
    bank_doc_id = fields.Many2one('account.bank.docs', string='Bank Document', copy=False)
    
    
class AccountBankDocs(models.Model):
    _name = "account.bank.docs"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _description = "Bank Documents"
    _order = 'date desc, name desc, id desc'
    _check_company_auto = True

    READONLY_STATES = {
        'confirm': [('readonly', True)],
        'issue': [('readonly', True)],
        'expire': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    @api.model
    def _default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id')
    
    @api.model
    def _default_account_id(self):
        return self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')
    
    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()
    
    @api.model
    def _default_taxes_id(self):
        return self._default_product_id().taxes_id
    
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('issue', 'Issued'),
        ('expire', 'Expired'),
        ('close', 'Close'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    bank_ref = fields.Char(string='Bank Reference', copy=False)
    date = fields.Datetime(string='Date', required=True, index=True,   copy=False, default=fields.Datetime.now, help="Creation date of draft documents,\nConfirmation date of confirmed documents.")
    
    date_effective = fields.Datetime(string='Effective Date', required=True, index=True,   copy=False, default=fields.Datetime.now, help="Effective date expected from bank. ")
    date_issue = fields.Datetime(string='Issue On', copy=False, readonly=True, help="Issuance date of document from bank. ")

    
    date_schedule_expire = fields.Datetime(string='Expected Expiry', required=True, index=True,   copy=False, default=fields.Datetime.now, help="Schedule expiry of the document ")
    date_expire = fields.Datetime(string='Expired On', copy=False, readonly=True)

    user_id = fields.Many2one('res.users', string='Responsible', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]")
        
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,   default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,   default=lambda self: self.env.company.id)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain=[('type', '=', 'bank')])
    product_id = fields.Many2one('product.product', string='Product', tracking=True,   domain="[('can_be_bank_document', '=', True)]", ondelete='restrict')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', compute='_compute_from_product_id_company_id',
        store=True, copy=True,   default=_default_product_uom_id, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True, string="UoM Category")
    allow_account_transaction = fields.Boolean(related='product_id.allow_account_transaction')
    
    amount = fields.Float("Amount", store=True, required=True, copy=True,   digits='Product Price')
    account_id = fields.Many2one('account.account', compute='_compute_from_product_id_company_id', store=True, readonly=False, string='Account', default=_default_account_id, domain="[('internal_type', '=', 'other'), ('company_id', '=', company_id)]", help="An  account is expected")
    tax_ids = fields.Many2many("account.tax", string="Taxes", compute='_compute_from_product_id_company_id', store=True, readonly=False, help="Taxes used for deposits", default=_default_taxes_id)
    
    account_move_ids = fields.One2many('account.move', 'bank_doc_id', string='Journal Entries')
    account_move_count = fields.Integer(string='Journal Entries', compute='_compute_account_move_ids')

    lead_id = fields.Many2one('crm.lead', string='Opportunity',   check_company=True, domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    note = fields.Html()
    
    @api.constrains('amount')
    def _check_amount(self):
        for order in self:
            if order.amount <= 0:
                raise UserError(_('The amount must be greated than 0'))
                
    @api.depends('product_id', 'company_id')
    def _compute_from_product_id_company_id(self):
        for acc in self.filtered('product_id'):
            acc = acc.with_company(acc.company_id)
            acc.product_uom_id = acc.product_id.uom_id
            account = acc.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                acc.account_id = account
    
    @api.depends('account_move_ids')
    def _compute_account_move_ids(self):
        for order in self:
            order.account_move_count = len(order.account_move_ids)
            
    
    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date']))
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('account.bank.docs', sequence_date=seq_date) or '/'
        res = super(AccountBankDocs, self_comp).create(vals)
        return res
    
    def _prepare_confirmation_values(self):
        return {
            'state': 'confirm',
            'date_effective': fields.Datetime.now()
        }
    
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for doc in self.filtered(lambda doc: doc.partner_id not in doc.message_partner_ids):
            doc.message_subscribe([doc.partner_id.id])
        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)
        
    
    def action_set_to_expire(self):
        self.update({
            'state': 'expire'
        })
    
    def _get_forbidden_state_confirm(self):
        return {'done', 'cancel'}                
    
    
    def _get_payment_details(self, order):
        context = {'lang': order.partner_id.lang}
        amount = order.amount
        name = _("Bank document %s of %s") % (self.product_id.name, self.amount)
        
        del context
        return amount, name
    
    
    def create_invoice(self):
        order = self
        amount, name = self._get_payment_details(order)
        #name = 'this is test'
        #amount = self.amount
        move_type = self._context.get('move_type')
        invoice_vals = self._prepare_invoice_values(order, name, amount,move_type)
        
        if self.state == 'confirm':
            self.write({
                'state':'issue',
                'date_issue': fields.Datetime.now(),
            })
        elif self.state == 'expire':
            self.write({
                'state':'close',
                'date_expire': fields.Datetime.now(),
            })
        self.activity_update()
        
        
        invoice = self.env['account.move'].with_company(order.company_id)\
            .sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice
    
    def _prepare_invoice_values(self, order, name, amount,move_type):
        
        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id).get_fiscal_position(order.partner_id.id)
        
        invoice_vals = {
            'ref': order.bank_ref,
            'move_type': move_type,
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_id.id,
            #'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'fiscal_position_id': fpos,
            'partner_shipping_id': order.partner_id.id,
            'currency_id': order.currency_id.id,
            'payment_reference': order.bank_ref,
            'invoice_payment_term_id': order.partner_id.property_supplier_payment_term_id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'bank_doc_id': order.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'tax_ids': fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == order.company_id)).ids,
                #'tax_ids': [(6, 0, so_line.tax_id.ids)],
                #'sale_line_ids': [(6, 0, [so_line.id])],
                #'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                #'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals
    
    def action_view_invoice(self):
        invoices = self.mapped('account_move_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
        return action
    
    def activity_update(self):
        #for bank in self.filtered(lambda hol: hol.state in ['confirm','issue']):
        for bank in self:
            self.activity_schedule(
                'de_sale_account_docs.mail_act_document_approval',
                user_id=self.env.user.id)
        self.filtered(lambda hol: hol.state == 'issue').activity_feedback(['de_sale_account_docs.mail_act_document_approval'])
        self.filtered(lambda hol: hol.state in ('close', 'cancel')).activity_unlink(['de_sale_account_docs.mail_act_document_approval'])
