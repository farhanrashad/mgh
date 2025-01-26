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

def get_loan(flag = 0):
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    product = request.env['product.product'].search([('can_be_expensed','=',True)])
    loan_type = request.env['hr.employee.loan.type'].search([])
    
    
    return {
        'employees' : employees,
        'product' : product,
        'loan_type': loan_type,
        
    }

class DePortalLoan(http.Controller):
    @http.route('/my/loan', type='http', auth='public', website=True)
    def loan_webform(self, **kw):
        return http.request.render('de_portal_loan.from_portal_loan', get_loan())
    
    
    
    @http.route('/create/loan', type='http', auth='public', website=True)
    def create_loan(self, **kw):
        loan_val = {
            'name': kw.get('name'),
            'manager_id': kw.get('manager_id'),
            'loan_type_id': kw.get('loan_type_id'),
            'amount': kw.get('amount'),
            'date_start': kw.get('date_start'),
            'installments': kw.get('installments'),
            'date_end':  kw.get('date_end'),
            'product_id': int(kw.get('product_id')),
            'interest_rate': kw.get('interest_rate'),
            'ref': kw.get('ref'),
            'date': fields.date.today(),
            
        }
        record = request.env['hr.employee.loan'].sudo().create(loan_val)
        record.compute_loan()
        record.action_submit_request()
        return request.render('de_portal_loan.loan_thankx', {})
    
    
    
class CustomerPortal(CustomerPortal):
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'loan_count' in counters:
            values['loan_count'] = request.env['hr.employee.loan'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  

    @http.route(['/advance/loan', '/advance/loan/page/<int:page>'], type='http', auth="user", website=True)
    def portal_advance_loan(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Reason'), 'order': 'reason desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft','submit', 'validate','approved','post','close','done','cancel'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'validate': {'label': _('Validated'), 'domain': [('state', '=', 'validate')]},
            'submit': {'label': _('Submitted'), 'domain': [('state', '=', 'submit')]},  
            'approved': {'label': _('Approved'), 'domain': [('state', '=', 'approved')]},
            'post': {'label': _('Posted'), 'domain': [('state', '=', 'post')]}, 
            'done': {'label': _('Paid'), 'domain': [('state', '=', 'done')]},
            'close': {'label': _('Closed'), 'domain': [('state', '=', 'close')]},
            'cancel': {'label': _('Refused'), 'domain': [('state', '=', 'cancel')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in Sequence')},
            'reason': {'input': 'name', 'label': _('Search in Reason')},
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
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
            
            
        domain += [('employee_id.user_id','=',http.request.env.context.get('uid'))] 
        loan_count = request.env['hr.employee.loan'].search_count(domain)

        pager = portal_pager(
            url="/advance/loan",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=loan_count,
            page=page,
            step=self._items_per_page
        )

        loan = request.env['hr.employee.loan'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        grouped_loan = [loan]
                
       
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_loan': grouped_loan,
            'page_name': 'loan',
            'default_url': '/advance/loan',
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
        return request.render("de_portal_loan.portal_hr_loan", values)
    
    
   

    
    
    
        
          
