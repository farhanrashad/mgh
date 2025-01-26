# -*- coding: utf-8 -*-
# from odoo import http


# class DeProjectStageApprovals(http.Controller):
#     @http.route('/de_project_stage_approvals/de_project_stage_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_project_stage_approvals/de_project_stage_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_project_stage_approvals.listing', {
#             'root': '/de_project_stage_approvals/de_project_stage_approvals',
#             'objects': http.request.env['de_project_stage_approvals.de_project_stage_approvals'].search([]),
#         })

#     @http.route('/de_project_stage_approvals/de_project_stage_approvals/objects/<model("de_project_stage_approvals.de_project_stage_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_project_stage_approvals.object', {
#             'object': obj
#         })
