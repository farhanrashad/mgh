from odoo import models,fields,api,_


class InheritedAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    validated_by = fields.Char()



    def action_validated_by(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['account.analytic.line'].browse(selected_ids)
        selected_records .sudo().write({'validated_by': user.name})

