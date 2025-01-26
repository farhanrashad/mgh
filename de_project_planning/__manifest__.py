# -*- coding: utf-8 -*-
{
    'name': "Project Planning & Control",

    'summary': """
          Project Planning & Control
           """,

    'description': """
          Project Planning & Control
          ==========================
          Cost Sheet
          Job Order
          Requisition
          
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
    'category': 'project',
    'version': '18.0.1.8',

    'depends': ['base', 'project','stock','account','hr_timesheet','purchase_requisition_stock'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'data/project_planning_data.xml',
        #'wizard/stock_picking_project_location_wizard_views.xml',
        #'views/menu_item.xml',
        #'views/product_views.xml',
        #'views/note_views.xml',
        #'views/stock_location_views.xml',
        #'views/stock_move_views.xml',
        #'views/purchase_views.xml',
        #'views/purchase_requisition_views.xml',
        #'views/stock_picking_views.xml',
        #'views/project_views.xml',
        #'views/job_order_views.xml',
        #'views/project_cost_sheet_views.xml',
        #'views/account_budget_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
