# -*- coding: utf-8 -*-
# from odoo import http


# class DeShippingPaymentTerms(http.Controller):
#     @http.route('/de_shipping_payment_terms/de_shipping_payment_terms/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_shipping_payment_terms/de_shipping_payment_terms/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_shipping_payment_terms.listing', {
#             'root': '/de_shipping_payment_terms/de_shipping_payment_terms',
#             'objects': http.request.env['de_shipping_payment_terms.de_shipping_payment_terms'].search([]),
#         })

#     @http.route('/de_shipping_payment_terms/de_shipping_payment_terms/objects/<model("de_shipping_payment_terms.de_shipping_payment_terms"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_shipping_payment_terms.object', {
#             'object': obj
#         })
