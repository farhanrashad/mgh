# -*- coding: utf-8 -*-
{
    'name': "Task Workflow",

    'summary': """
        Task Workflow through stages
        """,

    'description': """
        Project Task Workflow
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
    'category': 'Project',
    'version': '18.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
