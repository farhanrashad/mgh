# -*- coding: utf-8 -*-
{
    'name': "Employee Financial",

    'summary': """
    Core Employee Accounting
        """,

    'description': """
        Employee Accounting Core
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resources',
    'version': '18.0.0.3',

    'depends': ['hr','hr_contract'],

    'data': [
        'views/hr_menu_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
