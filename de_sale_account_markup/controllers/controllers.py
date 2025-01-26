# -*- coding: utf-8 -*-
# from odoo import http


# class DeSaleAccountMarkup(http.Controller):
#     @http.route('/de_sale_account_markup/de_sale_account_markup/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_sale_account_markup/de_sale_account_markup/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_sale_account_markup.listing', {
#             'root': '/de_sale_account_markup/de_sale_account_markup',
#             'objects': http.request.env['de_sale_account_markup.de_sale_account_markup'].search([]),
#         })

#     @http.route('/de_sale_account_markup/de_sale_account_markup/objects/<model("de_sale_account_markup.de_sale_account_markup"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_sale_account_markup.object', {
#             'object': obj
#         })
