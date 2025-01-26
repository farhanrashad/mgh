{
    "name": "Purchase Order Wizard",
    "category": 'Purchase',
    "summary": '',
    "description": """Sale Order Wizard on Purchase Order""",
    "sequence": 0,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '18.0.0.1',
    "depends": ['base', 'purchase', 'sale','stock'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/stock_enhancement_wizard.xml',
        'wizards/po_enhancement_wizard.xml',
        'views/po_enhancement_view.xml',

    ],
    "price": 25,
    "currency": 'PKR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
