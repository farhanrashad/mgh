# -*- coding: utf-8 -*-

{
    "name": "Sale Quotation Report",
    'version': '14.0.0.0',
    "category": 'Sale',
    "summary": ' Print with #, without # and without BOQ reports in Sale Quotation',
    'sequence': 1,
    "description": """"  """,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'license': 'LGPL-3',
    'depends': ['base', 'sale'],
    'data': [
        'report/sale_quotation_report.xml',
        'views/sale_quotation.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
