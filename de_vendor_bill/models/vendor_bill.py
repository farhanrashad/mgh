# -*- coding: utf-8 -*-
#################################################################################
# Author      : Dynexcel (<https://dynexcel.com/>)
# Copyright(c): 2015-Present dynexcel.com
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
################################################################################
from odoo.exceptions import Warning
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    def send_approval_button(self):
        self.write({
            'state': 'to approve'
        })

    def send_first_approval_button(self):
        self.write({
            'state': 'first approve'
        })

    def button_first_approved(self):
        self.write({
            'state': 'first approve'
        })

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', '2nd Approval'),
        ('send first approval', 'Send For First Approval'),
        ('first approve', '1st Approval'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)



class PaymentState(models.Model):
    _name = 'account.vendor_bill_state'
    _description = 'Vendor Bill State'

    name = fields.Char(string='Bill Status',help='maintain the states of the payment document')
    authority = fields.Many2one('res.groups')

class account_payment(models.Model):
    _inherit = 'account.move'
    
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', '2nd Approval'),
        ('send first approval', 'Send For First Approval'),
        ('first approve', '1st Approval'),
        ('purchase', 'Purchase Order'),
        ('posted', 'Posted'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    def send_first_approval_button(self):
        self.write({
            'state': 'first approve'
        })
        
    def button_first_approved(self):
        self.write({
            'state': 'first approve'
        })
        
    def button_draft(self):
        self.write({
            'state': 'draft'
        })

        
    def send_approval_button(self):
        self.write({
            'state': 'to approve'
        })
        
    def button_second_approved(self):
        self.write({
            'state': 'posted'
        })
        
        
#     def button_second_approved(self):
#         self.message_post(body=_('Dear %s, bill has posted') % (self.env.user.name,),
#                               partner_ids=[self.env.user.partner_id.id])
#         res = super(account_payment, self).action_post()
      
#         return res
        
    def button_cancel(self):
        self.write({
            'state': 'cancel'
        })
        
    def button_done(self):
        self.write({
            'state': 'done'
        })

