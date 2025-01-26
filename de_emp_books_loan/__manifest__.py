# -*- coding: utf-8 -*-
{
    'name': "Employee Loan",

    'summary': """
    Employee Loan 
        """,

    'description': """
        Employee Loan
        - Installment
        - Disbursments
      
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    'category': 'Employee',
    'version': '18.0.0.7',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','de_emp_books','account'],

    # always loaded
    'data': [
        'security/hr_loan_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_data.xml',
        'views/res_config_settings_views.xml',
        'views/loan_menuitems.xml',
        'wizard/hr_loan_refuse_reason_views.xml',
        'wizard/hr_loan_refund_wizard_views.xml',
        'views/loan_type_views.xml',
        'views/loan_views.xml',
        'views/loan_deferred_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'live_test_url': 'https://youtu.be/aD9UZlYM58o',
    'price': 25,
    'currency': 'USD',
    'images': ['static/description/banner.jpg'],
}
