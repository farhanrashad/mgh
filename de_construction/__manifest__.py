# -*- coding: utf-8 -*-
{
    'name': "Construction Project",

    'summary': """
          Construction Management System
           """,

    'description': """
          Construction Management System
          1-Job Order 
          2- Project have multiple task
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'stock', 'account', 'purchase'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'wizards/con_create_sub_tasks.xml',
        # 'reports/con_job_order_notes.xml',
        # 'reports/con_job_order_notes_template.xml',
        # 'reports/con_job_order_report.xml',
        # 'reports/con_job_order_template.xml',
        # 'reports/con_projects_template.xml',
        # 'reports/con_projects_report.xml',
        'views/con_project_task_type.xml',
        'views/con_config.xml',
        'data/sequence.xml',
        'views/con_job_order.xml',
        'views/con_materials_boq.xml',
        'views/con_project.xml',
        'views/con_vendor.xml',
        'views/con_project_notes.xml',
        'views/con_boq.xml',
        'views/con_job_order_notes.xml',
        'views/menu_item.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
