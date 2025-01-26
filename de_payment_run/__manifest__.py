# -*- coding: utf-8 -*-
{
    'name': "Payment Automation",

    'summary': "Payment Run - Payment Automation Program",

    'description': """
Payment run program streamlines financial operations by automating the collection and disbursement of payments. It allows businesses to schedule and execute payment runs efficiently, ensuring timely payments to vendors and seamless collection from customers. Say goodbye to manual payment processing hassles and embrace the convenience and accuracy of automated payment management with Odoo's robust module.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'support': "info@dynexcel.com",
    'category': 'Sales/Subscriptions',
    'version': '18.0.0.5',
    'live_test_url': 'https://youtu.be/_E8akhA1KXs',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_run_views.xml',
        'views/payment_run_line_views.xml',
        'views/res_partner_views.xml',
        'data/ir_cron_data.xml',
        'reports/ir_actions_report.xml',
        'reports/ir_actions_report_templates.xml',
        'wizards/bank_assignment_wizard_views.xml',
        'wizards/include_invoices_wizard_views.xml',
    ],
    'license': 'OPL-1',
    'price': 50,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

