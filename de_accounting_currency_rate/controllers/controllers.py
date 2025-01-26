# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountingCurrencyRate(http.Controller):
#     @http.route('/de_accounting_currency_rate/de_accounting_currency_rate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_accounting_currency_rate/de_accounting_currency_rate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_accounting_currency_rate.listing', {
#             'root': '/de_accounting_currency_rate/de_accounting_currency_rate',
#             'objects': http.request.env['de_accounting_currency_rate.de_accounting_currency_rate'].search([]),
#         })

#     @http.route('/de_accounting_currency_rate/de_accounting_currency_rate/objects/<model("de_accounting_currency_rate.de_accounting_currency_rate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_accounting_currency_rate.object', {
#             'object': obj
#         })
