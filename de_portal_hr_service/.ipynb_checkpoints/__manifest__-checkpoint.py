# -*- coding: utf-8 -*-
{
    'name': "Employee Self Service",

    'summary': """
    Employee Self Service
        """,

    'description': """
        Employee Self Service
    """,
    'author': "dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Uncategorized',
    'version': '18.0.2.2',

    'depends': ['portal','de_emp_books','website_form','hr'],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_service_menu.xml',
        'views/hr_service_views.xml',
        #'views/hr_employee_views.xml',
        'views/hr_services_templates.xml',
        'views/hr_service_web_templates.xml',
        
        
    ],
   
}
