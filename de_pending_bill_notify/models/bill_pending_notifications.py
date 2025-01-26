from odoo import fields, models, _
from datetime import date, timedelta


class AccountMoveNotification(models.Model):
    _inherit = 'account.move'
    _description = ''

    def find_over_due_bill(self):
        current_date = date.today()
        notifications = self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('state', '=', 'draft')])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'To Do')])
        model_id =self.env['ir.model'].search([('model', '=', 'account.move')])
        for rec in notifications:
            if rec.invoice_date_due:
                delta = current_date - rec.invoice_date_due
                net_days = (delta.days - 7)
                net_days_factor = net_days / 10
                first_end_date = rec.invoice_date_due + timedelta(days=7)
                if first_end_date == current_date:
                    vals = {
                        'res_model_id': model_id.id,
                        'res_id': rec.id,  # bill id
                        'activity_type_id': activity_type.id,
                        'summary': 'Over Due Bill Alert!',
                        'date_deadline': current_date,
                        'automated': True,
                        'user_id': rec.create_uid.id,
                        'previous_activity_type_id': False,
                        'note': 'After Week Reminder\n You have not Paid your dues till today'}
                    obj = self.env['mail.activity'].create(vals)

                elif first_end_date < current_date:
                    # date_10th = rec.invoice_date_due + timedelta(days=17)
                    if net_days_factor==0:
                        vals = {
                            'res_model_id': model_id.id,
                            'res_id': rec.id,  # bill id
                            'activity_type_id': activity_type.id,
                            'summary': 'Over Due Bill Alert!',
                            'date_deadline': current_date,
                            'automated': True,
                            'user_id': rec.create_uid.id,
                            'previous_activity_type_id': False,
                            'note': 'After 10 Days Reminder\n You have not Paid your dues till today'}
                        obj = self.env['mail.activity'].create(vals)
