
from odoo import models, api, fields, _

class JobOrderReport(models.Model):
    _name = 'job.order'
    _description = 'job order model'

    @api.model
    def _get_report_values(self, decides, data=None):
        docs=self.env['job.order'].browse(decides[0])
        materialsplanning = self.env['material.planning.line'].search([('job_order_ref' ,'=' ,decides[0])])
        subtask = self.env['sub.tasks.line'].search([('sub_task_ref' ,'=' ,decides[0])])
        # stockmove = self.env['stock.move.line'].search([('ref_stock_move' ,'=' ,decides[0])])
        # stockmove_list = []
        # for i in stockmove:
        #     vals = {
        #         'expected_date': i.expected_date,
        #         'creation_date': i.creation_date,
        #         'source_document': i.source_document,
        #         'product_id': i.product_id,
        #         'initial_demand': i.initial_demand,
        #         'unit_of_measure': i.unit_of_measure,
        #         'state_check': i.state_check,
        #     }
        #     stockmove_list.append(vals)


        subtask_list = []
        for i in subtask:
            vals = {
                'title': i.title,
                'project_subtask': i.project_subtask,
                'assign_to': i.assign_to,
                'planned_hours': i.planned_hours,
                'remaining_hours': i.remaining_hours,
                'stage_subtask': i.stage_subtask,
            }
            subtask_list.append(vals)
            #material planning
        material_list = []
        for i in materialsplanning:
            vals = {
                'product_id': i.product_id,
                'name': i.name,
                'prod_quantity': i.product_uom_quantity,
                'unit_of_measure': i.product_uom
            }
            material_list.append(vals)
        return{
            'doc_model': 'job.order',
            'data': data,
            'docs': docs,
            'material_list': material_list,
            'subtask_list': subtask_list,
            # 'stockmove_list': stockmove_list,
        }

