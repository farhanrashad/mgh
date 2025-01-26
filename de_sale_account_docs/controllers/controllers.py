# -*- coding: utf-8 -*-
# from odoo import http


# class DeSaleAccountingDocuments(http.Controller):
#     @http.route('/de_sale_accounting_documents/de_sale_accounting_documents', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_sale_accounting_documents/de_sale_accounting_documents/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_sale_accounting_documents.listing', {
#             'root': '/de_sale_accounting_documents/de_sale_accounting_documents',
#             'objects': http.request.env['de_sale_accounting_documents.de_sale_accounting_documents'].search([]),
#         })

#     @http.route('/de_sale_accounting_documents/de_sale_accounting_documents/objects/<model("de_sale_accounting_documents.de_sale_accounting_documents"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_sale_accounting_documents.object', {
#             'object': obj
#         })
