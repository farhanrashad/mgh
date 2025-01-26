# -*- coding: utf-8 -*-
{
    'name': "Purchase Tasks",

    'summary': """
    Purchase Tasks
            """,

    'description': """
        Purchase Milestones
        - Create Project
        - Create Tasks
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '18.0.2.4',

    # any module necessary for this one to work correctly
    'depends': ['purchase','de_project_task_workflow'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_task_template_views.xml',
        'views/project_views.xml',
        'views/project_task_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
