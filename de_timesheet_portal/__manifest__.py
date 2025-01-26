# -*- coding: utf-8 -*-
{
    'name': "Timesheet Portal",

    'summary': """
        Create timesheet from portal
        """,

    'description': """
        Create timesheet from portal
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",


    'category': 'web',
    'version': '18.0.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base','portal','web','project','hr_timesheet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv', 
        #'views/templates.xml',
         

    ]

}
