# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class ProjectSiteType(models.Model):
    _name = 'project.site.type'
    _description = 'Site Type'

    name = fields.Char('Site Type')


class ProjectJobType(models.Model):
    _name = "project.job.type"
    _description = "Job Type"
    _order = "sequence"

    name = fields.Char(string='Job Type', required=True, translate=True)
    sequence = fields.Integer(default=1)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    allow_site_planning = fields.Boolean(string='Site Planning')
    job_count = fields.Integer(compute='_compute_job_count', string="Task Count")
    project_notes_count = fields.Integer( string="Notes Count")

    site_type_id = fields.Many2one('project.site.type', string='Site Type')
    address_id = fields.Many2one('res.partner', string='Address')

    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
    location_id = fields.Many2one('stock.location', string='Stock Location', domain="[('site_location', '=', True)]")

    requisition_ids = fields.One2many('purchase.requisition', 'task_id', string='Requisitions', readonly=True, )
    requisition_count = fields.Integer(compute='_compute_purchase_requisition_count', string="Requisition Count")

    purchase_ids = fields.One2many('purchase.order', 'project_id', string='Purchases', readonly=True, )
    purchase_count = fields.Integer(compute='_compute_purchase_count', string="Purchase Count")

    picking_ids = fields.One2many('stock.picking', 'task_id', string='Pickings', readonly=True, )
    picking_count = fields.Integer(compute='_compute_picking_count', string="Picking Count")

    cost_sheet_ids = fields.One2many('project.cost.sheet', 'project_id', string='Cost Sheets', readonly=True, )
    cost_sheet_count = fields.Integer(compute='_compute_cost_sheet_count', string="Cost Sheet Count")

    sales_count = fields.Float(compute='_compute_sales_count', string='Sale Order')
    sales_amount = fields.Float(compute='_compute_sales_count', string='Sale Order')
    invoice_amount = fields.Float(compute='_compute_sales_count', string='Invoices')
    bill_count = fields.Integer(compute='_compute_sales_count', string='Vendor Bill')
    do_count = fields.Integer(compute='_compute_sales_count', string='Delivery Order')

    move_line_count = fields.Integer(compute='_compute_move_line_count', string="Move Count")

    def _compute_job_count(self):
        task_data = self.env['project.task'].read_group(
            [('project_id', 'in', self.ids), '|', '&', '&', ('stage_id.is_closed', '=', False),
             ('stage_id.fold', '=', False), ('is_job_order', '=', True), ('stage_id', '=', False)], ['project_id'],
            ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.job_count = result.get(project.id, 0)

    def _compute_notes_count(self):
        for project in self:
            project.project_notes_count = 1

    def _compute_purchase_requisition_count(self):
        project_data = self.env['purchase.requisition'].read_group([('project_id', 'in', self.ids)], ['project_id'],
                                                                   ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in project_data)
        for project in self:
            project.requisition_count = result.get(project.id, 0)

    def _compute_purchase_count(self):
        project_data = self.env['purchase.order'].read_group([('project_id', 'in', self.ids)], ['project_id'],
                                                             ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in project_data)
        for project in self:
            project.purchase_count = result.get(project.id, 0)

    def _compute_picking_count(self):
        project_data = self.env['stock.picking'].read_group([('project_id', 'in', self.ids)], ['project_id'],
                                                            ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in project_data)
        for project in self:
            project.picking_count = result.get(project.id, 0)

    def _compute_cost_sheet_count(self):
        project_data = self.env['project.cost.sheet'].read_group([('project_id', 'in', self.ids)], ['project_id'],
                                                                 ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in project_data)
        for project in self:
            project.cost_sheet_count = result.get(project.id, 0)

    def _compute_sales_count(self):
        cost_sheet_id = self.env['project.cost.sheet']
        Sale = self.env['sale.order']
        can_read = Sale.check_access_rights('read', raise_exception=False)
        for project in self:
            sale = self.env['sale.order'].search([('project_id', '=', project.id)])
            invoice = self.env['account.move'].search([('project_id', '=', self.id), ('move_type', '=', 'out_invoice')])
            vendor_bill_count = self.env['account.move'].search_count(
                [('project_id', '=', self.id), ('move_type', '=', 'in_invoice')])
            sale_count = self.env['sale.order'].search_count([('project_id', '=', project.id)])
            do_count = self.env['stock.picking'].search_count(
                [('picking_type_id', '=', 2), ('project_id', '=', self.id)])
            inv_amount = amount = 0
            for so in sale:
                amount = amount + so.amount_total
            for inv in invoice:
                inv_amount = inv_amount + inv.amount_total
            #             for bill in vendor_bill:
            #                 bill_amount = bill_amount + bill.amount_total
            cost_sheet_ids = self.env['project.cost.sheet'].search([('project_id', '=', project.id)])
            # project.sales_count = can_read and Sale.search_count([('id', 'in', cost_sheet_ids.sale_id.ids)]) or 0
            project.sales_count = can_read and Sale.search_count([('project_id', '=', project.id)]) or 0
            project.sales_amount = amount
            project.invoice_amount = inv_amount
            project.bill_count = vendor_bill_count
            project.do_count = do_count

    def _compute_move_line_count(self):
        Move = self.env['stock.move.line']
        can_read = Move.check_access_rights('read', raise_exception=False)
        for project in self:
            project.move_line_count = can_read and Move.search_count([('project_id', '=', project.id)]) or 0

    def action_view_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")

        # pickings = self.mapped('picking_ids')
        moves = self.env['stock.move.line'].search([('project_id', '=', self.id), ])
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        elif moves:
            form_view = [(self.env.ref('stock.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = moves.id
        return action

    def action_view_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        cost_sheet_ids = self.env['project.cost.sheet'].search([('project_id', '=', self.id)])
        #         sales = self.env['sale.order'].search([('project_id','in',cost_sheet_ids.sale_id.ids),])
        sales = self.env['sale.order'].search([('project_id', '=', self.id), ])
        if len(sales) > 1:
            action['domain'] = [('id', 'in', sales.ids)]
        elif sales:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = sales.id
        return action

    def action_view_invoices(self):
        self.ensure_one()
        result= self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        result['domain']=[('project_id', '=', self.id), ('move_type', '=', 'out_invoice')]
        
        return result
        # return {
        #     'type': 'ir.actions.act_window',
        #     'binding_type': 'object',
        #     'domain': [('project_id', '=', self.id), ('move_type', '=', 'out_invoice')],
        #     'multi': False,
        #     'name': 'Invoice',
        #     'target': 'current',
        #     'res_model': 'account.move',
        #     'view_mode': 'list,form',
        # }

    def action_view_vendor_bill(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('project_id', '=', self.id), ('move_type', '=', 'in_invoice')],
            'multi': False,
            'name': 'Invoice',
            'target': 'current',
            'res_model': 'account.move',
            'view_mode': 'list,form',
        }

    def action_view_delivery_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('picking_type_id', '=', 2), ('project_id', '=', self.id)],
            'multi': False,
            'name': 'Invoice',
            'target': 'current',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
        }

    def action_view_sales1(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['domain'] = [('product_id', 'in', self.ids)]
        action['context'] = {
            # 'pivot_measures': ['product_uom_qty'],
            'active_id': self._context.get('active_id'),
            # 'search_default_Sales': 1,
            'active_model': 'sale.order',
            # 'time_ranges': {'field': 'date', 'range': 'last_365_days'},
        }
        return action


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_job_order = fields.Boolean(string='Is job order?')

    project_task_material_line = fields.One2many('project.task.material.line', 'task_id', string='Material Lines',
                                                 copy=True, auto_join=True)
    allow_site_planning = fields.Boolean(related='project_id.allow_site_planning')
    location_id = fields.Many2one('stock.location', related='project_id.location_id', )
    picking_type_id = fields.Many2one('stock.picking.type', related='project_id.picking_type_id', )

    requisition_ids = fields.One2many('purchase.requisition', 'task_id', string='Requisitions', readonly=True, )
    requisition_count = fields.Integer(compute='_compute_purchase_requisition_count', string="Requisition Count")

    picking_ids = fields.One2many('stock.picking', 'task_id', string='Pickings', readonly=True, )
    picking_count = fields.Integer(compute='_compute_picking_count', string="Picking Count")

    move_line_count = fields.Integer(compute='_compute_move_line_count', string="Move Count")

    # stock_move_ids = fields.One2many('stock.move', 'task_id', string='Task', readonly=True, domain="[('task_id','=',id),]" )

    task_notes_count = fields.Integer( string="Notes Count")

    # move_raw_ids = fields.One2many('stock.move', 'component_task_id', 'Components', copy=True, )

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('project.task.job.order') or _('New')
        result = super(ProjectTask, self).create(vals)
        return result



        self = self.with_company(self.company_id)


        self.partner_id = partner.id
        self.is_job_order = True
        self.name = 'New'
        name = self.name
        # Create Material Planning lines if necessary
        job_lines = []

        self.project_task_material_line = job_lines

    def _compute_notes_count(self):
        for task in self:
            task.task_notes_count = 1

    def _compute_purchase_requisition_count(self):
        task_data = self.env['purchase.requisition'].read_group([('task_id', 'in', self.ids)], ['task_id'], ['task_id'])
        result = dict((data['task_id'][0], data['task_id_count']) for data in task_data)
        for task in self:
            task.requisition_count = result.get(task.id, 0)

    def _compute_picking_count(self):
        task_data = self.env['stock.picking'].read_group([('task_id', 'in', self.ids)], ['task_id'], ['task_id'])
        result = dict((data['task_id'][0], data['task_id_count']) for data in task_data)
        for task in self:
            task.picking_count = result.get(task.id, 0)

    def _compute_move_line_count(self):
        Move = self.env['stock.move.line']
        can_read = Move.check_access_rights('read', raise_exception=False)
        for task in self:
            task.move_line_count = can_read and Move.search_count([('task_id', '=', task.id)]) or 0

    def action_view_move_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")

        # pickings = self.mapped('picking_ids')
        moves = self.env['stock.move.line'].search([('task_id', '=', self.id), ])
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        elif moves:
            form_view = [(self.env.ref('stock.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = moves.id
        return action


class ProjectTaskMaterialLine(models.Model):
    _name = 'project.task.material.line'
    _description = 'Job Order Material Planning'

    task_id = fields.Many2one('project.task', string='Task Reference', required=True, ondelete='cascade', index=True,
                              copy=False)
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain="[('purchase_ok', '=', True)]",
                                 change_default=True, ondelete='restrict')
    product_template_id = fields.Many2one('product.template', string='Product Template',
                                          related="product_id.product_tmpl_id", domain=[('purchase_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                  domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    qty_available = fields.Float(related='product_id.qty_available')
    date_scheduled = fields.Date(string='Scheduled Date')
    requisition_action = fields.Selection([
        ('purchase', 'Purchase'),
        ('transfer', 'Internal'),
    ], string='Requisition Action', default='purchase', ondelete='no action', store=True, required=True, readonly=False,
        compute='_compute_requisition_action')

    @api.depends('product_id', 'product_uom_qty', 'qty_available')
    def _compute_requisition_action(self):
        requisition_action = ''
        for line in self:
            if line.product_id:
                if (line.qty_available - line.product_uom_qty) > 0:
                    requisition_action = 'transfer'
                else:
                    requisition_action = 'purchase'
            else:
                requisition_action = 'purchase'
            line.requisition_action = requisition_action

    @api.onchange('product_id')
    def product_id_change(self):
        self.product_uom = self.product_id.uom_id.id
        self.name = self.product_id.product_tmpl_id.name

    def _prepare_purchase_requisition_line(self, name):
        self.ensure_one()
        task = self.task_id
        if self.name:
            line_name = self.name + name
        else:
            line_name = name
        return {
            # 'name': line_name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_po_id.id,
            'product_qty': self.product_uom_qty,
            'price_unit': 1,
            'schedule_date': self.date_scheduled,
            'account_analytic_id': task.project_id.analytic_account_id.id,
        }

    def _prepare_stock_move_line(self, name):
        self.ensure_one()
        task = self.task_id
        if self.name:
            line_name = self.name + name
        else:
            line_name = name
        return {
            'name': line_name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': self.product_uom_qty,
            # 'task_id': self.task_id.id,
            # 'project_id': self.task_id.project_id.id,
        }