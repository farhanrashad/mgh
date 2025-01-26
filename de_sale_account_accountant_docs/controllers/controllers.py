# -*- coding: utf-8 -*-
# from odoo import http


# class DeSaleAccountAccountantDocs(http.Controller):
#     @http.route('/de_sale_account_accountant_docs/de_sale_account_accountant_docs', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_sale_account_accountant_docs/de_sale_account_accountant_docs/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_sale_account_accountant_docs.listing', {
#             'root': '/de_sale_account_accountant_docs/de_sale_account_accountant_docs',
#             'objects': http.request.env['de_sale_account_accountant_docs.de_sale_account_accountant_docs'].search([]),
#         })

#     @http.route('/de_sale_account_accountant_docs/de_sale_account_accountant_docs/objects/<model("de_sale_account_accountant_docs.de_sale_account_accountant_docs"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_sale_account_accountant_docs.object', {
#             'object': obj
#         })
