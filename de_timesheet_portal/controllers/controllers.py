from odoo import http, _,models,fields




from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND, OR
from operator import itemgetter
from pytz import timezone, UTC
# from odoo.addons.resource.models.resource import float_to_time
from collections import OrderedDict
from collections import namedtuple
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from odoo.tools import groupby as groupbyelem
from datetime import date, timedelta
# from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.account.controllers import portal
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal


class PortalTimesheet(CustomerPortal):



    @http.route(['/create/timesheet'], type='http', auth="user", website=True)
    def get_timesheet(self, **post):

        project = request.env['project.project'].sudo().search([('privacy_visibility','=','portal')])

        project_task = request.env['project.task'].sudo().search([])

        values = {

            'project_id':project,
            'project_task': project_task,
            'page_name': 'create_timesheet',
        }
        return request.render("de_timesheet_portal.portal_timesheet", values)

    @http.route(['/save/timesheet'], type='http', auth="user", website=True)
    def save_Timesheet(self, **kwargs):
        vals={}

        if kwargs.get('project'):
            vals.update({'project_id': int(kwargs.get('project'))})
        if kwargs.get('project_task'):
            vals.update({'task_id':int(kwargs.get('project_task'))})
            
        if kwargs.get('in_station'):
            vals.update({'x_studio_in_station': kwargs.get('in_station')})
        
        if kwargs.get('out_station'):
            vals.update({'x_studio_out_station': kwargs.get('out_station')})
        
        
        if kwargs.get('description'):
            vals.update({'name':kwargs.get('description')})

        if request.env.user.id:
            vals.update({'user_id':request.env.user.id})

        if kwargs.get('date'):
            vals.update({'date':str(kwargs.get('date'))})

        if kwargs.get('unit_amount'):
            vals.update({'unit_amount': kwargs.get('unit_amount')})



        request.env['account.analytic.line'].sudo().create(vals)
        return request.redirect('/my/timesheets')
    
    
    
# class deTimesheetPortal(TimesheetCustomerPortal):
    
    
    # @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='sol', **kw):
    #     res = super().portal_my_timesheets(page, sortby, filterby, search, search_in, groupby, **kw)
    #     return res
    
    #
    # @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):
    #     Timesheet_sudo = request.env['account.analytic.line'].sudo()
    #     values = self._prepare_portal_layout_values()
    #     domain = request.env['account.analytic.line']._timesheet_get_portal_domain()
    #     _items_per_page = 100
    #
    #     searchbar_sortings = {
    #         'date': {'label': _('Newest'), 'order': 'date desc'},
    #         'name': {'label': _('Description'), 'order': 'name'},
    #     }
    #
    #     searchbar_inputs = self._get_searchbar_inputs()
    #
    #     searchbar_groupby = self._get_searchbar_groupby()
    #
    #     today = fields.Date.today()
    #     quarter_start, quarter_end = date_utils.get_quarter(today)
    #     last_week = today + relativedelta(weeks=-1)
    #     last_month = today + relativedelta(months=-1)
    #     last_year = today + relativedelta(years=-1)
    #
    #     searchbar_filters = {
    #         'all': {'label': _('All'), 'domain': []},
    #         'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
    #         'week': {'label': _('This week'), 'domain': [('date', '>=', date_utils.start_of(today, "week")), ('date', '<=', date_utils.end_of(today, 'week'))]},
    #         'month': {'label': _('This month'), 'domain': [('date', '>=', date_utils.start_of(today, 'month')), ('date', '<=', date_utils.end_of(today, 'month'))]},
    #         'year': {'label': _('This year'), 'domain': [('date', '>=', date_utils.start_of(today, 'year')), ('date', '<=', date_utils.end_of(today, 'year'))]},
    #         'quarter': {'label': _('This Quarter'), 'domain': [('date', '>=', quarter_start), ('date', '<=', quarter_end)]},
    #         'last_week': {'label': _('Last week'), 'domain': [('date', '>=', date_utils.start_of(last_week, "week")), ('date', '<=', date_utils.end_of(last_week, 'week'))]},
    #         'last_month': {'label': _('Last month'), 'domain': [('date', '>=', date_utils.start_of(last_month, 'month')), ('date', '<=', date_utils.end_of(last_month, 'month'))]},
    #         'last_year': {'label': _('Last year'), 'domain': [('date', '>=', date_utils.start_of(last_year, 'year')), ('date', '<=', date_utils.end_of(last_year, 'year'))]},
    #     }
    #     # default sort by value
    #     if not sortby:
    #         sortby = 'date'
    #     order = searchbar_sortings[sortby]['order']
    #     # default filter by value
    #     if not filterby:
    #         filterby = 'all'
    #     domain = AND([domain, searchbar_filters[filterby]['domain']])
    #
    #     if search and search_in:
    #         domain += self._get_search_domain(search_in, search)
    #
    #     timesheet_count = Timesheet_sudo.search_count(domain)
    #     # pager
    #     pager = portal_pager(
    #         url="/my/timesheets",
    #         url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby, 'groupby': groupby},
    #         total=timesheet_count,
    #         page=page,
    #         step=_items_per_page
    #     )
    #
    #     def get_timesheets():
    #         groupby_mapping = self._get_groupby_mapping()
    #         field = groupby_mapping.get(groupby, None)
    #         orderby = '%s, %s' % (field, order) if field else order
    #         timesheets = Timesheet_sudo.search(domain, order=orderby, limit=_items_per_page, offset=pager['offset'])
    #         if field:
    #             if groupby == 'date':
    #                 time_data = Timesheet_sudo.read_group(domain, ['date', 'unit_amount:sum'], ['date:day'])
    #                 mapped_time = dict([(datetime.strptime(m['date:day'], '%d %b %Y').date(), m['unit_amount']) for m in time_data])
    #                 grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k]) for k, g in groupbyelem(timesheets, itemgetter('date'))]
    #             else:
    #                 time_data = time_data = Timesheet_sudo.read_group(domain, [field, 'unit_amount:sum'], [field])
    #                 mapped_time = dict([(m[field][0] if m[field] else False, m['unit_amount']) for m in time_data])
    #                 grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k.id]) for k, g in groupbyelem(timesheets, itemgetter(field))]
    #             return timesheets, grouped_timesheets
    #
    #         grouped_timesheets = [(
    #             timesheets,
    #             sum(Timesheet_sudo.search(domain).mapped('unit_amount'))
    #         )] if timesheets else []
    #         return timesheets, grouped_timesheets
    #
    #     timesheets, grouped_timesheets = get_timesheets()
    #
    #     is_admin =True
    #     if request.env.user.name !='Administrator':
    #         is_admin= False
    #     values.update({
    #         'timesheets': timesheets,
    #         'grouped_timesheets': grouped_timesheets,
    #         'page_name': 'timesheet',
    #         'default_url': '/my/timesheets',
    #         'pager': pager,
    #         'searchbar_sortings': searchbar_sortings,
    #         'search_in': search_in,
    #         'search': search,
    #         'sortby': sortby,
    #         'groupby': groupby,
    #         'searchbar_inputs': searchbar_inputs,
    #         'searchbar_groupby': searchbar_groupby,
    #         'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
    #         'filterby': filterby,
    #         'is_admin':is_admin,
    #         'is_uom_day': request.env['account.analytic.line']._is_timesheet_encode_uom_day(),
    #     })
    #     return request.render("hr_timesheet.portal_my_timesheets", values)
    #
    #

    
class AccountAnalyticTimeSheetInherit(models.Model):
    _inherit = 'account.analytic.line'  
    def monthRange(self):
        input_dt = datetime.now().date()#- relativedelta(months=1)
        date_to = input_dt
        # f_day=input_dt.replace(day=1)
        # next_month = input_dt.replace(day=28) + timedelta(days=4)
        # l_day = next_month - timedelta(days=next_month.day)
        date_from = date_to - timedelta(days=30)
        return date_from,date_to
    def _timesheet_get_portal_domain(self):  
        portal_domain = super(AccountAnalyticTimeSheetInherit ,self)._timesheet_get_portal_domain()
        f_day,l_day = self.monthRange()
        if self.env.user.name != 'Administrator' :
            user_domain =[('employee_id.user_id', 'in', [self.env.user.id])]
            user_domain +=[('date','>=',f_day),('date','<=',l_day)]
            portal_domain += user_domain
        return portal_domain
    
    
