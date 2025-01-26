{
    "name": "Product Vendor Price",
    "category": 'Products',
    "summary": 'Add Product Vendor Price',
    "description": """


    """,
    "sequence": 0,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '18.0.0.1',
    "depends": ['base','product', 'purchase', 'sale', 'stock'],
    "data": [
        'data/schedule_action.xml',
        'views/product_vendor_price_view.xml',
        # 'security/ir.model.access.csv',

    ],

    "price": 25,
    "currency": 'PKR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
