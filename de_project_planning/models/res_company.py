# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # -------------------------------------------------------------------------
    # Sequences
    # -------------------------------------------------------------------------
    def _create_internal_requisition_sequence(self):
        requisition_vals = []
        for company in self:
            requisition_vals.append({
                'name': 'Internal Requisition (%s)' % company.name,
                'code': 'stock.internalrequisition',
                'company_id': company.id,
                'prefix': 'IR/',
                'padding': 5,
            })
        if requisition_vals:
            self.env['ir.sequence'].create(requisition_vals)

    @api.model
    def create_missing_internal_requisition_sequence(self):
        company_ids = self.env['res.company'].search([])
        company_has_internal_requisition_seq = self.env['ir.sequence'].search([('code', '=', 'stock.internalrequisition')]).mapped('company_id')
        company_todo_sequence = company_ids - company_has_internal_requisition_seq
        company_todo_sequence._create_internal_requisition_sequence()

    def _create_per_company_sequences(self):
        super(ResCompany, self)._create_per_company_sequences()
        self._create_internal_requisition_sequence()

    # -------------------------------------------------------------------------
    # Picking types
    # -------------------------------------------------------------------------
    def _create_internal_requisition_picking_type(self):
        requisition_vals = []
        for company in self:
            sequence = self.env['ir.sequence'].search([
                ('code', '=', 'stock.internalrequisition'),
                ('company_id', '=', company.id),
            ])
            requisition_vals.append({
                'name': 'Requisition',
                'company_id': company.id,
                'warehouse_id': False,
                'sequence_id': sequence.id,
                'code': 'internal',
                #'default_location_src_id': self.env.ref('stock.stock_location_stock').id,
                #'default_location_dest_id': self.env.ref('stock.stock_location_stock').id,
                'sequence_code': 'IR',
            })
        if requisition_vals:
            self.env['stock.picking.type'].create(requisition_vals)

    @api.model
    def create_missing_internal_requisition_picking_type(self):
        company_ids = self.env['res.company'].search([])
        company_has_internal_requisition_picking_type = (
            self.env['stock.picking.type']
            .search([
                ('default_location_src_id.usage', '=', 'internal'),
                ('default_location_dest_id.usage', '=', 'internal'),
            ])
            .mapped('company_id')
        )
        company_todo_picking_type = company_ids - company_has_internal_requisition_picking_type
        company_todo_picking_type._create_internal_requisition_picking_type()

    def _create_per_company_picking_types(self):
        super(ResCompany, self)._create_per_company_picking_types()
        self._create_internal_requisition_picking_type()
