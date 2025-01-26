# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    @api.model
    def default_get(self, fields):
        result = super(ProductTemplate, self).default_get(fields)
        if self.env.context.get('default_can_be_bank_document'):
            result['supplier_taxes_id'] = False
        return result

    can_be_bank_document = fields.Boolean(string="Can be Bank Document", compute='_compute_can_be_bank_document',
        store=True, readonly=False, help="Specify whether the product can be selected in an bank document.")
    
    allow_account_transaction = fields.Boolean(string="Allow Accounting Transaction", help="Allow to generate accounting entries for bank document")

    @api.depends('type')
    def _compute_can_be_bank_document(self):
        self.filtered(lambda p: p.type not in ['consu', 'service']).update({'can_be_bank_document': False})