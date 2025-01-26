# -*- coding: utf-8 -*-
{
    'name': "Account Bank Document Enterprise",

    'summary': """
    Account Bank Document Enterprise
        """,

    'description': """
        Account Bank Document Enterprise
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant','de_sale_account_docs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/account_accountant_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
