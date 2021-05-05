from odoo import api, fields, models
from odoo.exceptions import UserError


class ScopeWork(models.Model):
    _name = 'scope.work'

    name = fields.Char(string="Scope Title")
    description = fields.Text(string="Description")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    scope_id = fields.Many2one('scope.work', string="Please Select Your Scope of work")
    scope_description = fields.Text('Description')

    @api.onchange('scope_id')
    def onchange_scope_id(self):
        self.scope_description = self.scope_id.description
