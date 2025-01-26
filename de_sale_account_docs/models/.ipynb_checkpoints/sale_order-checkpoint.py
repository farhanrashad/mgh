# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    bank_doc_ids = fields.Many2many('account.bank.docs', string='Financial Documents', compute='_compute_bank_doc_ids')
    bank_doc_count = fields.Integer(string='Bank Docs', compute='_compute_bank_doc_ids')
    
    @api.depends('bank_doc_ids')
    def _compute_bank_doc_ids(self):
        bank_documents = self.env['account.bank.docs'].browse()
        for order in self:
            bank_documents = self.env['account.bank.docs'].search([('lead_id','=',order.opportunity_id.id)])
            order.bank_doc_ids = bank_documents.ids
            order.bank_doc_count = len(bank_documents)
            
            
    def action_view_documents(self):
        return self._get_action_view_documents(self.bank_doc_ids)
    
    def _get_action_view_documents(self, docs):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env["ir.actions.actions"]._for_xml_id("de_sale_account_docs.action_account_bank_docs")

        if len(docs) > 1:
            action['domain'] = [('id', 'in', docs.ids)]
        elif docs:
            form_view = [(self.env.ref('de_sale_account_docs.account_bank_dosc_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = docs.id
        # Prepare the context.
        #fin_doc_id = docs.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        #if fin_doc_id:
        #    fin_doc_id = fin_doc_id[0]
        #else:
        #    fin_doc_id = docs[0]
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id, )
        return action



    
