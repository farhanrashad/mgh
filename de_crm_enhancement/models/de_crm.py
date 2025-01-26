from odoo import api, fields, models, _

from odoo.exceptions import UserError


class CrmEnhancement(models.Model):
    _inherit = 'crm.lead'

    client_information = fields.Boolean(string="Client Information", default=True)
    requirements = fields.Boolean(string="Requirements")
    specification = fields.Boolean(string="Specification")
    drawing = fields.Boolean(string="Drawing")
    deadline = fields.Boolean(string="Deadline")
    
    
    
