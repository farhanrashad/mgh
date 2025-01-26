
# # -*- coding: utf-8 -*-

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from operator import itemgetter
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR



def get_advance_salary(flag = 0):
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    advance_type = request.env['hr.employee.advance.type'].sudo().search([], limit=1)
    available_amount = request.env['hr.employee.advance'].sudo().search([], limit=1)
#     analytic_account = request.env['account.analytic.account'].search([])
    return {
        'employees' : employees,
        'success_flag' : flag,
        'company_info': company_info,
        'advance_type': advance_type,
        'available_amount': available_amount,
#         'analytic_account': analytic_account,
        
        
    }



class Salary(http.Controller):
    
    @http.route('/salary_webform', type='http', auth='public', website=True)
    def salary_webform(self, **kw):
         return http.request.render('de_portal_adavance_salary.create_advance_salary',get_advance_salary())
        
        
    @http.route('/create/salary_webform', type='http', auth='public', website=True)
    def create_webrequest(self, **kw):
        salary_val = {
            'advance_type_id':request.env['hr.employee.advance.type'].sudo().search([], limit=1).id,
#             'analytic_account_id':request.env['account.analytic.account'].sudo().search([], limit=1).id,
            'ref':  kw.get('ref'),
            'amount': kw.get('amount'),
            'name': kw.get('name'),
            'allow_exceeded_limit': kw.get('allow_exceeded_limit'),
            'applicable_amount':request.env['hr.employee.advance'].sudo().search([], limit=1).id,
            'date':  fields.date.today(),
            'date_due':kw.get('date_due'),
        }
        record = request.env['hr.employee.advance'].sudo().create(salary_val)
        record.action_submit_advance()
        return request.render('de_portal_adavance_salary.request_thanks', {})
        
        
        
        
        
        
        
        
        
class CustomerPortal(CustomerPortal):
    

    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'advance_count' in counters:
            values['advance_count'] = request.env['hr.employee.advance'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  

    @http.route(['/advance/salary', '/advance/salary/page/<int:page>'], type='http', auth="user", website=True)
    def portal_advance_salary(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Reason'), 'order': 'reason desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'submit','approved','post','done','close', 'cancel'])]},
            'draft': {'label': _('To Submit'), 'domain': [('state', '=', 'draft')]},
            'submit': {'label': _('Submitted'), 'domain': [('state', '=', 'submit')]},  
            'approved': {'label': _('Waiting Approval'), 'domain': [('state', '=', 'approved')]},
            'post': {'label': _('Posted'), 'domain': [('state', '=', 'post')]}, 
            'done': {'label': _('Paid'), 'domain': [('state', '=', 'done')]},
            'close': {'label': _('Closed'), 'domain': [('state', '=', 'close')]},
            'cancel': {'label': _('Refused'), 'domain': [('state', '=', 'cancel')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in Sequence')},
            'reason': {'input': 'reason', 'label': _('Search in Reason')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')}, 
            'advance': {'input': 'amount', 'label': _('Search in Amount')},
            'date': {'input': 'date', 'label': _('Search in Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }


        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])

            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
            
        domain += [('employee_id.user_id','=',http.request.env.context.get('uid'))]            
        expense_count = request.env['hr.employee.advance'].search_count(domain)

        pager = portal_pager(
            url="/advance/salary",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=expense_count,
            page=page,
            step=self._items_per_page
        )
        

        domain += [('employee_id.user_id', '=', http.request.env.context.get('uid'))]
        adv_salary = request.env['hr.employee.advance'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['advance_salary_history'] = adv_salary.ids[:100]

        grouped_adv_salary = [adv_salary]
                
       
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_adv_salary': grouped_adv_salary,
            'page_name': 'Advance Salary',
            'default_url': '/advance/salary',
            'pager': pager,
            'company_info': company_info,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            
        })
        return request.render("de_portal_adavance_salary.portal_advance_salary", values)
     
        
        
        
# class CreateAdvanceSalary(http.Controller):
    
#     @http.route('/advance/salary/create/',type="http", website=True, auth='user')
#     def action_advance_salary(self, **kw):
#         return request.render("de_portal_adavance_salary.create_advance_salary",get_advance_salary())
    
#     @http.route('/advance/salary/save', type="http", auth="public", website=True)
#     def action_create_advance_salary(self, **kw):
#         expense_val = {
#             'reason': kw.get('description'),
#             'employee_id': int(kw.get('employee_id')),
#             'advance': kw.get('advance_amount'),
#             'date':  fields.date.today(),
#         }
#         record = request.env['hr.employee.advance'].sudo().create(expense_val)
#         return request.render("de_portal_adavance_salary.advance_salary_submited", {})
    