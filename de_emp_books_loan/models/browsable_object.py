#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields


class BrowsableObject(object):
    def __init__(self, employee_id, dict, env):
        self.employee_id = employee_id
        self.dict = dict
        self.env = env

    def __getattr__(self, attr):
        return attr in self.dict and self.dict.__getitem__(attr) or 0.0

    def __getitem__(self, key):
        return self.dict[key] or 0.0

class Loans(BrowsableObject):
    """a class that will be used into the python code, mainly for usability purposes"""

    def sum(self, from_date, to_date=None):
        if to_date is None:
            to_date = fields.Date.today()
        self.env.cr.execute("""SELECT sum(amount)
                    FROM hr_employee_loan as ln, hr_employee_loan_line as ll
                    WHERE ln.employee_id = %s AND ln.state = 'done'
                    AND ln.date_start >= %s AND ln.date_end <= %s AND ln.id = ll.employee_loan_id""",
                    (self.employee_id, from_date, to_date))
        res = self.env.cr.fetchone()
        return res and res[0] or 0.0
