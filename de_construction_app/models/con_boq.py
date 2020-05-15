# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class MeterialBoq(models.Model):
    _name = 'meterial.boq'
    _description = 'this is boq model'
    _rec_name = 'name'

    def con_create_picking(self):
        for rec in self:
            rec.state = 'created'

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

    name = fields.Char(string='Number', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('construction.requistions.sequence') or _('New')
        result = super(MeterialBoq, self).create(vals)
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
            # 'domain': [('opportunity_id', '=', self.id)],
            # 'context': dict(self._context, create=True, default_opportunity_id=self.id),
        }

    state = fields.Selection(
        [('draft', 'New'),
         ('waiting', 'Waiting Department Approval'),
         ('ir', 'Waiting IR Approval'),
         ('approved', 'approved'),
         ('created', 'Purchase Order Created'),
         ('recived', 'Recived')], string='Status', default='draft', index=True)

    con_internal_picking = fields.Char(string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_purchase_order = fields.Char(string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_picking_count = fields.Char(string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_order_count = fields.Char(string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(comodel_name="res.partner", string="Employee", required=False, readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one(comodel_name="job.order", string="Department", required=False, readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(comodel_name='res.company', string="Company", required=True,readonly=True, states={'draft': [('readonly', False)]})
    responsible_id = fields.Many2one(comodel_name="con.projects", string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    job_order = fields.Char(string="Task / Job Order User", required=False, readonly=True, states={'draft': [('readonly', False)]})
    requistion_date = fields.Datetime(string="Requstion Date", required=False, readonly=True, states={'draft': [('readonly', False)]})
    recive_date = fields.Datetime(string="Recive Date", required=False, readonly=True, states={'draft': [('readonly', False)]})
    req_deadline = fields.Datetime(string="Requistion Deadline", required=False, readonly=True, states={'draft': [('readonly', False)]})
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one(comodel_name="con.projects", string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    task_id = fields.Many2one(comodel_name="con.projects", string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_requistion_line = fields.One2many(comodel_name="meterial.boq.line", inverse_name="req_line", string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    con_picking_details_line = fields.One2many(comodel_name="meterial.picking.line", inverse_name="picking_line", string="", required=False, readonly=True, states={'draft': [('readonly', False)]})
    picking_ids = fields.Many2one(comodel_name="job.order", string="", required=False, )
