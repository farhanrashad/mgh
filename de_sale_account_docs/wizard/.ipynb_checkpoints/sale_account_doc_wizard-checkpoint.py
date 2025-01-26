# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta


class SaleAccountDocWizard(models.TransientModel):
    _name = "sale.account.docs.wizard"
    _description = "Sale Accounting Documents Wizard"
    _check_company_auto = True

    #@api.model
    #def _count(self):
    #    return len(self._context.get('active_ids', []))
    
    @api.model
    def _default_currency_id(self):
        if self._context.get('active_model') == 'crm.lead' and self._context.get('active_id', False):
            crm_lead = self.env['crm.lead'].browse(self._context.get('active_id'))
            return crm_lead.company_id.currency_id

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()
    
    @api.model
    def _default_account_id(self):
        return self._default_product_id()._get_product_accounts()['expense']

    @api.model
    def _default_taxes_id(self):
        return self._default_product_id().taxes_id
        
    
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain=[('type', '=', 'bank')])
    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('can_be_bank_document', '=', True)])
    currency_id = fields.Many2one('res.currency', string='Currency', default=_default_currency_id)
    amount = fields.Monetary('Amount', required=True, help="The amount to be invoiced, taxes excluded.")
    account_id = fields.Many2one("account.account", string="Account", compute='_compute_from_product_id_company_id', store=True, readonly=False, domain=[('deprecated', '=', False)],
        help="Account used for deposits", default=_default_account_id)
    taxes_id = fields.Many2many("account.tax", string="Taxes", compute='_compute_from_product_id_company_id', store=True, readonly=False, help="Taxes used for deposits", default=_default_taxes_id)
    bank_ref = fields.Char(string='Bank Reference', copy=False)
    date_effective = fields.Datetime(string='Effective Date', required=True, default=fields.Datetime.now, help="Effective date expected from bank. ")
    date_expire = fields.Datetime(string='Expiry Date', required=True, default=fields.Datetime.now, help="Effective date expected from bank. ")

    
    @api.depends('product_id')
    def _compute_from_product_id_company_id(self):
        for bank in self.filtered('product_id'):
            lead = self.env['crm.lead'].browse(self._context.get('active_id'))
            bank = bank.with_company(lead.company_id)
            bank.taxes_id = bank.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == lead.company_id)  # taxes only from the same company
            account = bank.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                bank.account_id = account
                
    def _create_financial_document(self, lead, amount):
        vals = self._prepare_document_values(lead, amount)
        
        bank_doc = self.env['account.bank.docs'].with_company(lead.company_id)\
            .sudo().create(vals).with_user(self.env.uid)
        bank_doc.message_post_with_view('mail.message_origin_link',
                    values={'self': bank_doc, 'origin': lead},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return bank_doc
    
    def create_financial_document(self):
        crm_leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
        
        for lead in crm_leads:
            taxes = self.product_id.taxes_id.filtered(lambda r: not lead.company_id or r.company_id == lead.company_id)
            tax_ids = taxes.ids
            
            #so_line_values = self._prepare_so_line(lead, analytic_tag_ids, tax_ids, amount)
            #so_line = sale_line_obj.create(so_line_values)
            amount = self.amount
            self._create_financial_document(lead, amount)
            
        if self._context.get('open_documents', False):
            return crm_leads.action_view_documents()
        return {'type': 'ir.actions.act_window_close'}
    
    def _prepare_document_values(self, lead, amount):
        doc_vals = {
            'bank_ref': self.bank_ref,
            'partner_id': lead.partner_id.id,
            'date': fields.Date.today(),
            'date_effective': self.date_effective,
            'date_expire': self.date_expire,
            'currency_id': lead.company_id.currency_id.id,
            'company_id': lead.company_id.id,
            'journal_id': self.journal_id.id,
            'product_id': self.product_id.id,
            'amount': amount,
            'account_id': self.account_id.id,
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'lead_id': lead.id,
            'state':'draft',
        }

        return doc_vals
