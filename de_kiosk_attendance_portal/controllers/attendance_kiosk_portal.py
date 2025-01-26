# # -*- coding: utf-8 -*-
from . import config
from . import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from operator import itemgetter
from datetime import datetime , date
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
import base64
import binascii

def kattendance_page_content(flag = 0):
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    return {
        'employees' : employees,
        'success_flag' : flag,
        'company_info' : company_info
    }
   
   


def paging(data, flag1 = 0, flag2 = 0):        
    if flag1 == 1:
        return config.list12
    elif flag2 == 1:
        config.list12.clear()
    else:
        k = []
        for rec in data:
            for ids in rec:
                config.list12.append(ids.id)        
 
    
        
class CreateKAttendance(http.Controller):

    @http.route('/kattendance/create/checkin',type="http", website=True, auth='user')
    def kattendance_create_checkin(self, **kw):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        employee_id = kattendance_page_content()['employees']
        
        att_exists = request.env['hr.attendance'].search([('employee_id','=', employee_id.id),('check_out','=',False)], order='check_in desc', limit=1)
        if att_exists:
            print(att_exists.check_in)
            return request.render("de_kiosk_attendance_portal.already_checkin_exists",kattendance_page_content()) 
        
        else:    
            att_val = {
                'employee_id': employee_id.id,            
                'check_in': current_datetime,
            }
            record = request.env['hr.attendance'].sudo().create(att_val)
            return request.render("de_kiosk_attendance_portal.kattendance_checkin_template",kattendance_page_content()) 
    
    @http.route('/kattendance/create/checkout',type="http", website=True, auth='user')
    def kattendance_create_checkout(self, **kw):
        print('datetime.now()',datetime.now())
        print('datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")',datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        employee_id = kattendance_page_content()['employees']
        att_exists = request.env['hr.attendance'].search([('employee_id','=', employee_id.id),('check_out','=',False)])
        
        if att_exists:
            att_val = {
                'check_out':current_datetime,
            }
            record = att_exists.sudo().write(att_val)
            return request.render("de_kiosk_attendance_portal.kattendance_checkin_template",kattendance_page_content()) 
        else:
            return request.render("de_kiosk_attendance_portal.no_checkin_exists",kattendance_page_content()) 

    
    
    @http.route('/my/resignation/save', type="http", auth="public", website=True)
    def resignation_submit_forms(self, **kw):
        if kw.get('description'):
            resignation_val = {
                'employee_id': int(kw.get('employee_id')),            
                'resignation_type':kw.get('resignation_type'),
                'resignation_reason': kw.get('resignation_reason'),
                'expected_revealing_date': kw.get('last_day_of_employee'),
                'reason':kw.get('description'),
            }
            record = request.env['hr.resignation'].sudo().create(resignation_val)
            
        return request.render("de_kiosk_attendance_portal.kattendance_submitted", {}, kattendance_page_content())
  

    
    
    
class CustomerPortal(CustomerPortal):

    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'kattendance_count' in counters:
            values['kattendance_count'] = request.env['hr.attendance'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _resignation_get_page_view_values(self,kattendance, next_id = 0,pre_id= 0, kattendance_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name': 'kisok attendance',
            'kattendance': kattendance,
            'kattendance_user_flag':kattendance_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(kattendance, access_token, values, 'my_timeoff_history', False, **kwargs)
    

    @http.route(['/my/kattendance', '/my/kattendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_kattendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        print('----------------in py method')
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            
#             'draft': {'label': _('To Submit'), 'domain': [('state', '=', 'draft')]},
#             'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},  
#             'confirm': {'label': _('Confirmed'), 'domain': [('state', '=', 'confirm')]},
#             'approved': {'label': _('Refused'), 'domain': [('state', '=', 'approved')]}, 
        }
                                 
        
        searchbar_inputs = {  
            'name': {'input': 'name', 'label': _('Search in Employee')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

#         timeoff_groups = request.env['hr.resignation'].search([])

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
            domain += search_domain
        kattendance_count = request.env['hr.attendance'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/kattendance",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _kattendance = request.env['hr.attendance'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_timeoff_history'] = _kattendance.ids[:100]

        grouped_kattendances = [_kattendance]
        grouped_check_in = True
        grouped_check_out = False
                
        paging(0,0,1)
        paging(grouped_kattendances)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_kattendances': grouped_kattendances,
            'grouped_check_in': grouped_check_in,
            'grouped_check_out': grouped_check_out,
            'page_name': 'Kiosk Attendance',
            'default_url': '/my/kattendance',
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
        return request.render("de_kiosk_attendance_portal.portal_my_kattendances", values)   

   
#     @http.route(['/my/resignation/<int:resignation_id>'], type='http', auth="user", website=True)
#     def portal_my_resignation(self, resignation_id, access_token=None, **kw):
#         try:
#             resignation_sudo = self._document_check_access('hr.resignation', resignation_id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
# 
#         next_id = 0
#         pre_id = 0
#         resignation_user_flag = 0
#                  
#         resignation_id_list = paging(0,1,0)
#         next_next_id = 0
#         resignation_id_list.sort()
#         length_list = len(resignation_id_list)
#         length_list = length_list - 1
#         if length_list != 0:
#             if resignation_id in resignation_id_list:
#                 resignation_id_loc = resignation_id_list.index(resignation_id)
#                 if resignation_id_loc == 0:
#                     next_id = 1
#                     pre_id = 0
#                 elif resignation_id_loc == length_list:
#                     next_id = 0
#                     pre_id = 1
#                 else:
#                     next_id = 1
#                     pre_id = 1
#         else:
#             next_id = 0
#             pre_id = 0
#  
#  
#         values = self._resignation_get_page_view_values(resignation_sudo,next_id, pre_id,access_token, **kw) 
#         return request.render("de_kiosk_attendance_portal.portal_my_resignation", values)
#  
#     @http.route(['/resignation/next/<int:resignation_id>'], type='http', auth="user", website=True)
#     def portal_my_next_resignation(self, resignation_id, access_token=None, **kw):
#          
#         resignation_id_list = paging(0,1,0)
#         next_next_id = 0
#         resignation_id_list.sort()
#          
#         length_list = len(resignation_id_list)
#         if length_list == 0:
#             return request.redirect('/my')
#         length_list = length_list - 1
#          
#         if resignation_id in resignation_id_list:
#             resignation_id_loc = resignation_id_list.index(resignation_id)
#             next_next_id = resignation_id_list[resignation_id_loc + 1] 
#             next_next_id_loc = resignation_id_list.index(next_next_id)
#             if next_next_id_loc == length_list:
#                 next_id = 0
#                 pre_id = 1
#             else:
#                 next_id = 1
#                 pre_id = 1      
#         else:
#             buffer_larger = 0
#             buffer_smaller = 0
#             buffer = 0
#             for ids in resignation_id_list:
#                 if ids < timeoff_id:
#                     buffer_smaller = ids
#                 if ids > timeoff_id:
#                     buffer_smaller = ids
#                 if buffer_larger and buffer_smaller:
#                     break
#             if buffer_larger:
#                 next_next_id = buffer_smaller
#             elif buffer_smaller:
#                 next_next_id = buffer_larger
#                  
#             next_next_id_loc = resignation_id_list.index(next_next_id)
#             length_list = len(resignation_id_list)
#             length_list = length_list + 1
#             if next_next_id_loc == length_list:
#                 next_id = 0
#                 pre_id = 1
#             elif next_next_id_loc == 0:
#                 next_id = 1
#                 pre_id = 0
#             else:
#                 next_id = 1
#                 pre_id = 1
#           
#         values = []
#         active_user = http.request.env.context.get('uid')
#         id = resignation_id
#         try:
#             resignation_sudo = self._document_check_access('hr.resignation', next_next_id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
#          
#  
#         values = self._resignation_get_page_view_values(resignation_sudo,next_id, pre_id, access_token, **kw) 
#         return request.render("de_kiosk_attendance_portal.portal_my_resignation", values)
#  
#    
#     @http.route(['/resignation/pre/<int:resignation_id>'], type='http', auth="user", website=True)
#     def portal_my_pre_resignation(self, resignation_id, access_token=None, **kw):
#          
#         resignation_id_list = paging(0,1,0)
#         pre_pre_id = 0
#         resignation_id_list.sort()
#         length_list = len(resignation_id_list)
#      
#         if length_list == 0:
#             return request.redirect('/my')
#          
#         length_list = length_list - 1
#         if resignation_id in resignation_id_list:
#             resignation_id_loc = resignation_id_list.index(resignation_id)
#             pre_pre_id = resignation_id_list[resignation_id_loc - 1] 
#             pre_pre_id_loc = resignation_id_list.index(resignation_id)
#  
#             if resignation_id_loc == 1:
#                 next_id = 1
#                 pre_id = 0
#             else:
#                 next_id = 1
#                 pre_id = 1      
#         else:
#             buffer_larger = 0
#             buffer_smaller = 0
#             buffer = 0
#             for ids in resignation_id_list:
#                 if ids < resignation_id:
#                     buffer_smaller = ids
#                 if ids > resignation_id:
#                     buffer_smaller = ids
#                 if buffer_larger and buffer_smaller:
#                     break
#             if buffer_smaller:
#                 pre_pre_id = buffer_smaller
#             elif buffer_larger:
#                 pre_pre_id = buffer_larger
#                  
#             pre_pre_id_loc = resignation_id_list.index(pre_pre_id)
#             length_list = len(resignation_id_list)
#             length_list = length_list -1
#             if pre_pre_id_loc == 0:
#                 next_id = 1
#                 pre_id = 0
#             elif pre_pre_id_loc == length_list:
#                 next_id = 0
#                 pre_id = 1
#             else:
#                 next_id = 1
#                 pre_id = 1
#     
#         values = []
#  
#         id = pre_pre_id
#         try:
#             resignation_sudo = self._document_check_access('hr.resignation', pre_pre_id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
#          
#         resignation_user_flag = 0
#  
#  
#         values = self._resignation_get_page_view_values(resignation_sudo, next_id,pre_id, access_token, **kw) 
#         return request.render("de_kiosk_attendance_portal.portal_my_resignation", values)
