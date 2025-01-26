# -*- coding: utf-8 -*-
{
    'name': "Employee Book Archive Buttons",

    'summary': """
        Prepayments to employees for Expenses
        """,
    'description': """
         Expense prepayments app allow to post prepayments to employees and reimburse payments with expenses. This app is integrated and dependent with employee expenses app. 
    """,
    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
    'category': 'Human Resources/Expenses',
    'version': '18.0.0.3',
    'depends': ['base','hr_expense','account','de_emp_books','de_emp_books_expense_prepayments'],
    'data': [
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'live_test_url': 'https://www.youtube.com/watch?v=Ymwohz8QawM&t=25s',
    'price': 55,
    'currency': 'USD',
    'images': ['static/description/banner.jpg'],
}
