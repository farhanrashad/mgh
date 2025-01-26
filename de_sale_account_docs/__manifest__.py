# -*- coding: utf-8 -*-
{
    'name': "Financial Documents",

    'summary': """
    Financial Documents e.g Bank guarantee
        """,

    'description': """
        Financial Documents e.g Bank guarantee
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Accounting/CRM/Sale',
    'version': '18.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['crm','sale_management','account'],

    'data': [
        'security/ir.model.access.csv',
        'data/financial_data.xml',
        #'data/mail_data.xml',
        'wizard/sale_account_doc_wizard_views.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/account_bank_docs_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
