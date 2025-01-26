{
    "name": "Purchase Order Status",
    "category": 'Purchase',
    "summary": 'Lock the quotations in Sales',
    "description": """


    """,
    "sequence": 0,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '18.0.0.1',
    "depends": ['purchase'],
    "data": [
        'views/purchase_order_status.xml',
        # 'security/ir.model.access.csv',

    ],

    "price": 25,
    "currency": 'PKR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
