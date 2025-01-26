# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Portal Attendance',
    'version': '18.0.0.1',
    'category': 'Attendance',
    'sequence': 10,
    'summary': 'Employee Attendance',
    'depends': [
        'hr_attendance',
        'portal',
        'rating',
        'resource',
        'web',
        'web_tour',
        'digest',
        'base',
        'hr_payroll',
    ],
    'description': "",
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_templates.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

