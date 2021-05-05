from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleTerm(models.Model):
    _name = 'sale.notes'

    name = fields.Char(string="Note Title")
    description = fields.Text(string="Description")

    # names = fields.Char('Note Description', invisible=True)
    # note_parent_id = fields.Many2one('sale.notes')


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    note_id = fields.Many2one('sale.notes', string="Please Select Your Note")
    note_description = fields.Text('Description')

    @api.onchange('note_id')
    def onchange_note_id(self):
        self.note_description = self.note_id.description


