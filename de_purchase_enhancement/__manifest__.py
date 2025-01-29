# -*- coding: utf-8 -*-
{
    'name': "Purchase Enhancement",
    'version': '18.0.0.3',
    'summary': """Purchase order based on sale order
    """,
    'sequence': '5',
    'description': """
    """,
    'category': 'Purchase',
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'depends': ['base', 'purchase', 'sale'],
    'data': [
        'views/purchase_view.xml',
        'views/sale_order_view.xml',
    ],

    'demo': [
    ],
    "installable": True,
}
