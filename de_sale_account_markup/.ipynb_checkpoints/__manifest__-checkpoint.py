# -*- coding: utf-8 -*-
{
    'name': "Sale Account Markup",

    'summary': """
    Martkup
        """,

    'description': """
        Markup
        - Sale
        - Account
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale/Accounting',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_views.xml',
        'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
