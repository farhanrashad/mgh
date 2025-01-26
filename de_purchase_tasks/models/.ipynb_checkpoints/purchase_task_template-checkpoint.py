# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



from werkzeug.urls import url_encode


class PurchaseTaskTemplate(models.Model):
    _name = 'purchase.task.template'
    _description = 'Purchase Task Template'

    name = fields.Char("Name", required=True)
    sequence = fields.Integer(string='Sequence', default=1, required=True, readonly=False, compute='_compute_sequence', store=True)
    order_type_id = fields.Many2one('purchase.order.type', string="Order Type", )
    completion_days = fields.Integer(string='Completion Days')
    approval_days = fields.Integer(string='Approval Days')
    completion_percent = fields.Float(string='Completion Percentage')
    stage_ids = fields.Many2many('project.task.type', string='Stages', required=True)
    allow_picking = fields.Boolean(string='Allow on Picking', help='User will provide the milestone on picking with purchase order reference')
    allow_invoice = fields.Boolean(string='Allow on invoice', help='User will provide the milestone on invoice with purchase order reference')

    user_id = fields.Many2one('res.users', string='Responsible', index=True, default=lambda self: self.env.user, check_company=True)

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    template_doc_ids = fields.One2many('purchase.task.template.docs', 'purchase_task_template_id', string='Docs', copy=True)

    @api.constrains('completion_percent')
    def _check_completion_percent(self):
        for line in self:
            if line.completion_percent > 100:
                raise UserError(_('The percentage cannot be greater than 100'))
                
    @api.depends('order_type_id')
    def _compute_sequence(self):
        count = self.env['purchase.task.template'].search_count([('order_type_id','=',self.order_type_id.id)])
        self.sequence = count + 1
    
class PurchaseTaskTemplateDocs(models.Model):
    _name = 'purchase.task.template.docs'
    _description = 'Purchase Task Template docs'
    
    name = fields.Char("Name", required=True)
    purchase_task_template_id = fields.Many2one('purchase.task.template', string='Template', index=True, required=True, ondelete='cascade')
