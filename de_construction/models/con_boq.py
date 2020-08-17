# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
from datetime import datetime, timedelta


class PurchaseOrderVendors(models.Model):
    _name = 'purchase.vendor'

    vendor_id = fields.Many2one(comodel_name='purchase.order.wizard')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Name', required=True)
    phone = fields.Char(string='Phone', related='partner_id.phone')
    email = fields.Char(string='Email', related='partner_id.email')


class PurchaseOrderProd(models.Model):
    _name = 'order.products'

    order_product_id = fields.Many2one(comodel_name='purchase.order.wizard')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')
    product_uom = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure')
    on_hand_qty = fields.Float(string='Quantity On Hand')


class PurchaseOrderWizard(models.Model):
    _name = 'purchase.order.wizard'

    vendor_ids = fields.One2many(comodel_name='purchase.vendor', inverse_name='vendor_id')
    order_product_ids = fields.One2many(comodel_name='order.products', inverse_name='order_product_id')
    wizard_exp = fields.Char()


class MaterialBoq(models.Model):
    _name = 'material.boq'
    _description = 'Material BOQ'
    _rec_name = 'name'

    def action_disposal(self):
        wizard_view_id = self.env.ref(
            'de_construction.purchase_order_wizard_view')
        return {
            'name': _('Purchase Order Wizard'),
            'res_model': 'purchase.order.wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_view_id.id,
            'target': 'new',
        }

    def con_create_picking(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']
        for line in self.con_requisition_line:
            if line.requisition_action == 'purchase_order':
                for vendor in line.vendor_id:
                    pur_order = purchase_order_obj.search(
                        [('requisition_po_id', '=', self.id), ('partner_id', '=', vendor.id)])
                    if pur_order:
                        po_line_vals = {
                            'product_id': line.product_id.id,
                            'product_qty': line.product_uom_qty,
                            'name': 'Product',
                            'price_unit': line.product_id.list_price,
                            'date_planned': datetime.now(),
                            'product_uom': line.product_uom.id,
                            'order_id': pur_order.id,
                        }
                        purchase_order_line = purchase_order_line_obj.create(po_line_vals)
                    else:
                        vals = {
                            'partner_id': vendor.id,
                            'date_order': datetime.now(),
                            'requisition_po_id': self.id,
                            'state': 'draft'
                        }
                        purchase_order = purchase_order_obj.create(vals)
                        po_line_vals = {
                            'product_id': line.product_id.id,
                            'product_qty': line.product_uom_qty,
                            'name': line.description,
                            'price_unit': line.product_id.list_price,
                            'date_planned': datetime.now(),
                            'product_uom': line.product_uom.id,
                            'order_id': purchase_order.id,
                        }
                        purchase_order_line = purchase_order_line_obj.create(po_line_vals)
                        print('l', purchase_order_line)

        res = self.write({
            'state': 'created',
        })
        return res

    def con_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_department_approval(self):
        for rec in self:
            rec.state = 'ir'

    def action_confirm(self):
        for rec in self:
            rec.state = 'waiting'

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def con_po_received(self):
        for rec in self:
            rec.state = 'received'
            rec.receive_date = fields.datetime.now()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('construction.requisitions.sequence') or _('New')
        result = super(MaterialBoq, self).create(vals)
        return result

    def con_internal_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'multi': False,
            'name': 'Estimate',
            'target': 'current',
            'res_model': 'meterial.boq',
            'view_mode': 'tree,form',
            'view_type': 'form',
        }

    @api.onchange('operation_type_id')
    def _onchange_picking_type(self):
        for rec in self:
            rec.source_location_id = rec.operation_type_id.default_location_src_id.id
            rec.destination_location_id = rec.operation_type_id.default_location_dest_id.id

    @api.onchange('task_id')
    def _onchange_task_id(self):
        for rec in self:
            rec.user_id = rec.task_id.assign_to.id
            rec.project_id = rec.task_id.project_id.id
            rec.analytic_account_id = rec.task_id.analytic_account_id.id

    def _get_purchase_order_count(self):
        for po in self:
            po_ids = self.env['purchase.order'].search([('requisition_po_id','=',po.id)])
            po.purchase_order_count = len(po_ids)

    def purchase_order_button(self):
        self.ensure_one()
        return {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('requisition_po_id', '=', self.id)],
        }

    state = fields.Selection(
        [('draft', 'New'),
         ('waiting', 'Waiting Department Approval'),
         ('ir', 'Waiting IR Approval'),
         ('approved', 'approved'),
         ('created', 'Purchase Order Created'),
         ('received', 'Received')], string='Status', default='draft', index=True)

    name = fields.Char(string='Number', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    con_internal_picking_name = fields.Char(string='', required=False, readonly=True,
                                            states={'draft': [('readonly', False)]})
    operation_type_id = fields.Many2one(comodel_name='stock.picking.type', string='Operation Type')
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='operation_type_id.code',
        readonly=True)
    source_location_id = fields.Many2one(comodel_name='stock.location', string='Source Location', required=True)
    destination_location_id = fields.Many2one(comodel_name='stock.location', string='Destination Location',
                                              required=False)
    source_document = fields.Char(sring='Source')
    con_purchase_order = fields.Char(string='', required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_picking_count = fields.Char(string='', required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_order_count = fields.Char(string='', required=False, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=False,
                                 readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one(comodel_name='hr.department', string='Department', required=False,
                                    readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=False, readonly=True,
                                 states={'draft': [('readonly', False)]})
    responsible_id = fields.Many2one(comodel_name='res.partner', string='', required=False, readonly=True,
                                     states={'draft': [('readonly', False)]})
    user_id = fields.Many2one(comodel_name='res.users', string='Task / Job Order User', required=False, readonly=True,
                              states={'draft': [('readonly', False)]})
    notes = fields.Text(string='Description')
    requisition_date = fields.Datetime(string='Requisition Date', required=False, readonly=True,
                                       states={'draft': [('readonly', False)]})
    receive_date = fields.Datetime(string='Receive Date', required=False, readonly=True,
                                   states={'draft': [('readonly', False)]})
    req_deadline = fields.Datetime(string='Requisition Deadline', required=False, readonly=True,
                                   states={'draft': [('readonly', False)]})
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account',
                                          readonly=True, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one(comodel_name='con.projects', string='', required=False, readonly=True,
                                 states={'draft': [('readonly', False)]})
    task_id = fields.Many2one(comodel_name='job.order', string='Task', required=False, readonly=True,
                              states={'draft': [('readonly', False)]})
    con_requisition_line = fields.One2many(comodel_name='material.boq.line', inverse_name='req_line', string='',
                                           required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_picking_details_line = fields.One2many(comodel_name='meterial.picking.line', inverse_name='picking_line',
                                               string='', required=False, readonly=True,
                                               states={'draft': [('readonly', False)]})
    picking_ids = fields.Many2one(comodel_name='job.order', string='', required=False)
    equipment_cost = fields.Float(string='Equipment / Machinery Cost')
    worker_cost = fields.Float(string='Worker / Resource Cost').a
    work_cost_package = fields.Float(string='Work Cost Package')
    subcontract_cost = fields.Float(string='Subcontract Cost')
    purchase_order_count = fields.Integer('Purchase Order', compute='_get_purchase_order_count')


class PurchaseOrderExt(models.Model):
    _inherit = 'purchase.order'

    requisition_po_id = fields.Many2one(comodel_name='material.purchase.requisition', string='Purchase Requisition')
