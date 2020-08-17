from odoo import api, fields, models


class JobNotes(models.Model):
    _name = 'job.notes'
    _description = 'this is job order notes model'


    def name_get(self):
        """ This method used to customize display name of the record """
        result = []
        for record in self:
            rec_name = "%s " % (record.note)
            result.append((record.id, rec_name))
        return result


    tag_ids = fields.Char(string='Tags')
    task_id = fields.Many2one('job.order', string='Task/ Job Order')
    project_id = fields.Many2one('con.projects', string='Construction Project')
    user_id = fields.Many2one('res.users', string='Responsible User')
    state = fields.Selection([
        ('new', 'New'),
        ('meeting_mint', 'Meeting Minutes'),
        ('notes', 'Notes'),
        ('todo', 'Todo'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='new')
    note = fields.Html(string="Description")
