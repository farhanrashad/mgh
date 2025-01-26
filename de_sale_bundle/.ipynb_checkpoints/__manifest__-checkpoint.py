{
    "name": "Sale Bundle",
    "category": 'Education',
    "summary": 'First Module test',
    "description": """


    """,
    "sequence": 0,
    "author": "Dynexcel_Internee",
    "website": "http://www.dynexcel.co",
    "version": '18.0.0.1',
    "depends": ['sale','base', 'sale_stock'],
    "data": [
        'views/product_bundle.xml',
        'security/ir.model.access.csv',
        # 'security/sale_security.xml',

    ],

    "price": 25,
    "currency": 'PKR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
