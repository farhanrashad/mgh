# -*- coding: utf-8 -*-
{
    'name': "Employee Advances",

    'summary': """
    Salary Advance
        """,

    'description': """
        Employee Salary Advance
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    'category': 'Employee',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','de_empfin_core','account'],

    # always loaded
    'data': [
        'security/hr_advance_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_data.xml',
        'data/payroll_data.xml',
        'report/advance_request_report.xml',
        'report/advance_report_templates.xml',
        'views/hr_job_views.xml',
        'views/hr_employee_views.xml',
        'views/advance_menuitems.xml',
        'wizard/hr_advance_refuse_reason_views.xml',
        'views/advance_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
