# -*- coding: utf-8 -*-
# from odoo import http


# class DeConstructionApp(http.Controller):
#     @http.route('/de_construction_app/de_construction_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_construction_app/de_construction_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_construction_app.listing', {
#             'root': '/de_construction_app/de_construction_app',
#             'objects': http.request.env['de_construction_app.de_construction_app'].search([]),
#         })

#     @http.route('/de_construction_app/de_construction_app/objects/<model("de_construction_app.de_construction_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_construction_app.object', {
#             'object': obj
#         })
