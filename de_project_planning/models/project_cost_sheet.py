# -*- coding: utf-8 -*-
from datetime import datetime, time
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

READONLY_STATES = {
        'confirm': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

class ProjectCostSheet(models.Model):
    _name = 'project.cost.sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cost Sheet'
    _order = 'date, id desc'
    _check_company_auto = True
    
    
    name = fields.Char(string='Reference', copy=False,   index=True, default=lambda self: _('New'))
    date = fields.Datetime(string='Date', required=True, index=True,   copy=False, default=fields.Datetime.now,)

    user_id = fields.Many2one('res.users', string="Request Owner",check_company=True, domain="[('company_ids', 'in', company_id)]", default=lambda self: self.env.user, required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related="user_id.employee_id")
    department_id = fields.Many2one('hr.department', string='Department',related="employee_id.department_id")
    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=4, default='draft')
    
    date_scheduled = fields.Date(string='Scheduled Date', index=True)
    




    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company,  )
    
    project_id = fields.Many2one('project.project', string='Project', required=True, check_company=True)
    sale_id = fields.Many2one('sale.order', string='Sale Order', copy=False)

    partner_id = fields.Many2one(related='project_id.partner_id', readonly=False,  )
    analytic_account_id = fields.Many2one('account.analytic.account')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,  
        default=lambda self: self.env.company.currency_id.id)
    description = fields.Text()
    jobs_count = fields.Integer(compute='_compute_jobs_count', string='Number of Jobs')

    material_cost_total = fields.Monetary(string='Material Cost', store=True, readonly=True, compute='_cost_all')
    labor_cost_total = fields.Monetary(string='Labor Cost', store=True, readonly=True, compute='_cost_all')
    overhead_cost_total = fields.Monetary(string='Overhead Cost', store=True, readonly=True, compute='_cost_all')
    cost_total = fields.Monetary(string='Total Cost', store=True, readonly=True, compute='_cost_all')

    select_all = fields.Boolean(string='Select All', default=False)
    
    def _cost_all(self):
        for project in self:
            material_cost = labor_cost = overhead_cost = 0.0
            for material in project.project_cost_sheet_material_line:
                material_cost += material.price_total
            for overhead in project.project_cost_sheet_overhead_line:
                overhead_cost += overhead.price_total
            for labor in project.project_cost_sheet_labor_line:
                labor_cost += labor.cost_total
            project.update({
                'material_cost_total': material_cost,
                'labor_cost_total': labor_cost,
                'overhead_cost_total': overhead_cost,
                'cost_total': material_cost + labor_cost + overhead_cost,
            })


    #order_count = fields.Integer(compute='_compute_orders_number', string='Number of Orders')

    @api.onchange('select_all')
    def _select_all(self):
        for line in self.project_cost_sheet_material_line:
            line.record_selection = self.select_all
                
    def _compute_jobs_count(self):
        for cost in self:
            cost.jobs_count = 0
    
    #@api.model
    def create1(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date']))
            vals['name'] = self.env['ir.sequence'].next_by_code('project.cost.sheet', sequence_date=seq_date) or _('New')
        result = super(ProjectCostSheet, self).create(vals)       
        return result
    
    
    def action_draft(self):
        self.state = 'draft'
    
    def action_confirm(self):
        self.ensure_one()
        if not self.project_cost_sheet_material_line:
            raise UserError(_("You cannot confirm cost sheet '%s' because there is no material line.", self.name))
        else:
            if self.name == 'New':
                self.update({
                    'name' : self.env['ir.sequence'].next_by_code('project.cost.sheet')
                })
            self.state = 'confirm'
        
    def action_done(self):
        """
        Generate all purchase order based on selected lines, should only be called on one agreement at a time
        """
        #if any(purchase_order.state in ['draft', 'sent', 'to approve'] for purchase_order in self.mapped('purchase_ids')):
            #raise UserError(_('You have to cancel or validate every RfQ before closing the purchase requisition.'))
        self.write({'state': 'done'})
        
    def action_cancel(self):
        self.state = 'cancel'
        
    def unlink(self):
        if any(requisition.state not in ('draft', 'cancel') for requisition in self):
            raise UserError(_('You can only delete draft requisitions.'))
        # Draft requisitions could have some requisition lines.
        self.mapped('purchase_demand_line').unlink()
        return super(PurchaseDemand, self).unlink()

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        if not self.sale_id:
            return

        self = self.with_company(self.company_id)
        sale = self.sale_id
        
        # Create material lines if necessary
        sheet_lines = []
        if self.project_cost_sheet_material_line:
            self.project_cost_sheet_material_line.unlink()
        
        if not self.partner_id.id:
            self.partner_id = self.sale_id.partner_id.id
            
        for line in sale.order_line.filtered(lambda r: r.display_type == False):
            # Create material line
            order_line_values = line._prepare_sale_order_line()
            sheet_lines.append((0, 0, order_line_values))
        self.project_cost_sheet_material_line = sheet_lines
    
class ProjectCostSheetMaterialLine(models.Model):
    _name = 'project.cost.sheet.material.line'
    _description = 'Cost Sheet Material Line'
    
    record_selection = fields.Boolean(string='Selection', default=False, copy=False)
    
    name = fields.Char(compute='_compute_line_name', string='Description', store=True, readonly=False, required=True)
    product_id = fields.Many2one('product.product', string='Product', domain="[('purchase_ok', '=', True),('type','!=','service')]", change_default=True, ondelete='restrict', required=True) 
    product_template_id = fields.Many2one('product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('purchase_ok', '=', True)])
    product_uom_qty = fields.Float(string='Planned Qty', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Uom', domain="[('category_id', '=', product_uom_category_id)]", required=True)
    currency_id = fields.Many2one('res.currency', store=True, string='Currency', readonly=True)
    standard_price = fields.Float(string='Cost/Unit', digits='Product Price', default=1)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    date_scheduled = fields.Date(string='Scheduled Date')
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    qty_received = fields.Float("Received Qty", compute='_compute_qty_received', compute_sudo=True, store=True, digits='Product Unit of Measure')
    qty_to_invoice = fields.Float(compute='_compute_qty_invoiced', string='To Invoice Quantity', store=True, readonly=True, digits='Product Unit of Measure')


    @api.depends('product_id')
    def _compute_qty_received(self):
        for line in self:
            line.qty_received = 0.0
    
    @api.depends('product_id')
    def _compute_qty_invoiced(self):
        for line in self:
            line.qty_to_invoice = 1
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        
        self.product_uom = self.product_id.uom_id.id
        self.standard_price = self.product_id.standard_price or 1.0
        self.name = self.product_id.description_purchase or self.product_id.name

    @api.depends('product_uom_qty', 'standard_price')
    def _compute_amount(self):
        for line in self:
            line.update({
                'price_total': line.product_uom_qty * line.standard_price,
            })
            

    def _compute_line_name(self):
        record.name = False
            
    def _prepare_job_order_material_line(self, name):
        self.ensure_one()
        if self.date_scheduled:
            date_planned = datetime.combine(self.date_scheduled, time.min)
        else:
            date_planned = datetime.now()
                
        return {
            'name': str(name) + ' ' + str(self.product_id.name),
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': self.product_uom_qty,
            'date_scheduled': date_planned,
        }
    
            
class ProjectCostSheetLaborLine(models.Model):
    _name = 'project.cost.sheet.labor.line'
    _description = 'Cost Sheet Labor Line'
    
    name = fields.Char(compute='_compute_line_name', string='Description', store=True, readonly=False)
    
    planned_hours = fields.Float("Initially Planned Hours", help='Time planned to achieve this task (including its sub-tasks).', tracking=True)
    total_timesheet_time = fields.Integer(compute='_compute_total_timesheet_time',
        help="Total number of time (in the proper UoM) recorded in the project, rounded to the unit.")
    #effective_hours = fields.Float("Hours Spent", compute='_compute_effective_hours', compute_sudo=True, store=True, help="Time spent on this task, excluding its sub-tasks.")
    #total_hours_spent = fields.Float("Total Hours", compute='_compute_total_hours_spent', store=True, help="Time spent on this task, including its sub-tasks.")
    currency_id = fields.Many2one('res.currency', store=True, string='Currency', readonly=True)
    hourly_cost = fields.Monetary('Cost/hr', currency_field='currency_id',
    	groups="hr.group_hr_user", default=1.0)
    cost_total = fields.Monetary(compute='_compute_all_cost', string='Total Cost', store=True)
    date_scheduled = fields.Date(string='Scheduled Date')
    
    @api.depends('planned_hours', 'hourly_cost')
    def _compute_all_cost(self):
        for line in self:
            line.update({
                'cost_total': line.planned_hours * line.hourly_cost,
            })
            
    def _compute_total_timesheet_time(self):
        self.total_timesheet_time = 0
            
    def _compute_line_name(self):
        #just in case someone opens the budget line in form view
        computed_name = ''
        record.name = computed_name
    
    
class ProjectCostSheetOverheadLine(models.Model):
    _name = 'project.cost.sheet.overhead.line'
    _description = 'Cost Sheet overhead Line'
    
    name = fields.Char(compute='_compute_line_name', string='Description', store=True, readonly=False, required=True)
    product_id = fields.Many2one('product.product', string='Product', domain="[('purchase_ok', '=', True),('type','=','service')]", change_default=True, ondelete='restrict', required=True) 
    product_template_id = fields.Many2one('product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('purchase_ok', '=', True)])
    product_uom_qty = fields.Float(string='Planned Qty', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Uom', domain="[('category_id', '=', product_uom_category_id)]", required=True)
    currency_id = fields.Many2one('res.currency', store=True, string='Currency', readonly=True)
    standard_price = fields.Float(string='Cost/Unit', digits='Product Price', default=1)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    date_scheduled = fields.Date(string='Scheduled Date')
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    qty_received = fields.Float("Received Qty", compute='_compute_qty_received', compute_sudo=True, store=True, digits='Product Unit of Measure')
    qty_to_invoice = fields.Float(compute='_compute_qty_invoiced', string='To Invoice Quantity', store=True, readonly=True, digits='Product Unit of Measure')


    @api.depends('product_id')
    def _compute_qty_received(self):
        for line in self:
            line.qty_received = 0.0
    
    @api.depends('product_id')
    def _compute_qty_invoiced(self):
        for line in self:
            line.qty_to_invoice = 1
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        
        self.product_uom = self.product_id.uom_id.id
        self.standard_price = self.product_id.standard_price or 1.0
        self.name = self.product_id.description_purchase or self.product_id.name
    
    @api.depends('product_uom_qty', 'standard_price')
    def _compute_amount(self):
        for line in self:
            line.update({
                'price_total': line.product_uom_qty * line.standard_price,
            })
            
    def _compute_line_name(self):
        #just in case someone opens the budget line in form view
        computed_name = ''
        record.name = computed_name