# -*- coding: utf-8 -*-

{
    "name": "CRM Enahancement",
    'version': '18.0.0.0',
    "category": 'CRM',
    "summary": 'CRM Enahancement',
    'sequence': -10,
    "description": """" CRM Enahancement """,
    'category': 'productivity',

    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'license': 'LGPL-3',
    'depends': ['base','crm'],
    'data': [
        'views/de_crm.xml',
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}
