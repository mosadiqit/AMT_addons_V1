# -*- coding: utf-8 -*-

from odoo import http, _, fields 
from odoo.http import request
from datetime import datetime, timedelta
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from odoo.exceptions import UserError

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        timesheets = request.env['account.analytic.line']
        timesheets_count = timesheets.search_count([
        ('user_id', 'child_of', [request.env.user.id])
          ])
        values.update({
        'timesheets_count': timesheets_count,
        })
        return values
    
    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timesheet(self, page=1, sortby=None, **kw):
        if not (request.env.user.has_group('base.group_user') and request.env.user.has_group('hr_timesheet.group_hr_timesheet_user')):
            return request.render("odoo_mobile_timesheet.not_allowed")
        response = super(CustomerPortal, self)
        values = {}
        timesheets_obj = http.request.env['account.analytic.line']
        domain = [
            ('user_id', 'child_of', [request.env.user.id]),
        ]
        # count for pager
        timesheets_count = http.request.env['account.analytic.line'].search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/timesheets",
            total=timesheets_count,
            page=page,
            step=self._items_per_page
        )
        sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'project': {'label': _('Project'), 'order': 'project_id'},
        }
        
        order = sortings.get(sortby, sortings['date'])['order']
        # content according to pager and archive selected
        domain += [('date', '=', kw.get('start_date'))] 
        timesheets = timesheets_obj.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.env.uid)])
        values.update({
            'employee_id' : employee_id,
            'timesheets': timesheets,
            'page_name': 'timesheets',
            'sortings' : sortings,
            'sortby': sortby,
            'pager': pager,
            'default_url': '/my/timesheets',
            'portal_timesheet':True,
            'timesheets_count': timesheets_count,
        })
        return request.render("odoo_mobile_timesheet.select_timesheets", values)
    
    @http.route(['/my/add_timesheet'], type='http', auth="user", website=True)
    def portal_add_timesheet(self, page=1, date_begin=None, date_end=None,
                             project=False, task=False, **kw):
        if not (request.env.user.has_group('base.group_user') and request.env.user.has_group('hr_timesheet.group_hr_timesheet_user')):
            return request.render("odoo_mobile_timesheet.not_allowed")

        project_ids = request.env['project.project'].search([('is_close', '=', False)])
        task_ids = request.env['project.task'].search([('stage_id.is_close', '=', False)])

        work_type_ids = request.env['timesheet.work.type'].search([])

        duration = kw.get('duration', '00:00')
        start_time = kw.get('start_time', '00:00')
        end_time = kw.get('end_time', '00:00')

        if project != 'False':
            project = int(project)

        if task != 'False':
            task =  int(task)

        values = {
            'project_ids': project_ids,
            'projects':project,
            'task_ids':task_ids,
            'tasks': task,
            'work_type_ids':work_type_ids,
            'portal_timesheet':True,
            'duration': duration,
            'start_time': start_time,
            'end_time': end_time,
        }
        if kw.get('timesheet_date'):
            values.update({'timesheet_date': kw.get('timesheet_date')})
        else:
            values.update({'timesheet_date': fields.Date.today()})
        return request.render("odoo_mobile_timesheet.add_new_timesheet", values)
    
    @http.route(['/my/create_new_timesheet'], type='http', auth="user", website=True)
    def create_new_timesheet(self, **kwargs):
        if not (request.env.user.has_group('base.group_user') and request.env.user.has_group('hr_timesheet.group_hr_timesheet_user')) or not kwargs:
            return request.render("odoo_mobile_timesheet.not_allowed")
        valse ={
            'user_id': request.env.user.id
        }
        if kwargs.get('project_id'):
            valse.update({'project_id': int(kwargs.get('project_id'))})
        if kwargs.get('task_id'):
            valse.update({'task_id': int(kwargs.get('task_id'))})
        if kwargs.get('work_type'):
            valse.update({'work_type_id': int(kwargs.get('work_type'))})
        if kwargs.get('start_time'):
            start = datetime.strptime(str(kwargs.get('start_time')),'%H:%M') - datetime.strptime(str('0:0'),'%H:%M')
            start_time = start.total_seconds()/3600.00
            valse.update({'start_time': start_time})
        if kwargs.get('end_time'):
            end = datetime.strptime(str(kwargs.get('end_time')),'%H:%M') - datetime.strptime(str('0:0'),'%H:%M')
            end_time = end.total_seconds()/3600.00
            valse.update({'end_time': end_time})
        if kwargs.get('is_billable'):
            if kwargs.get('is_billable') == 'on':
                valse.update({'is_billable': True})
            else:
                valse.update({'is_billable': False})
        if kwargs.get('is_paid'):
            if kwargs.get('is_paid') == 'on':
                valse.update({'is_paid': True})
            else:
                valse.update({'is_paid': False})
        if kwargs.get('description'):
            valse.update({'name': kwargs.get('description')})
        if kwargs.get('quantity'):
            quantity_str = str(kwargs.get('quantity'))
            try:
                date_tt = datetime.strptime(quantity_str,'%H:%M') - datetime.strptime(str('0:0'),'%H:%M')
            except:
                return request.render("odoo_mobile_timesheet.hour_usererror_msg")
            quantity = date_tt.total_seconds()/3600.00
            valse.update({'unit_amount': quantity})
        if kwargs.get('start_date'):
            date = datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d")
            valse.update({'date': date.date()})
        request.env['account.analytic.line'].create(valse)
        return request.redirect("/odoo_timesheet_portal_user_employee/select_timesheet?start_date="+str(kwargs.get('start_date')))


    @http.route(['/my/timesheet/<int:timesheet>'], type='http', auth="user", website=True)
    def edit_timesheet(self, timesheet=None, **kw):
        if not (request.env.user.has_group('base.group_user') and request.env.user.has_group('hr_timesheet.group_hr_timesheet_user')):
            return request.render("odoo_mobile_timesheet.not_allowed")
        analytic_line = request.env['account.analytic.line'].browse([timesheet])
        line_date = datetime.strptime(str(analytic_line.date), "%Y-%m-%d").strftime('%Y-%m-%d')
        work_type_ids = request.env['timesheet.work.type'].search([])
        values={
            'line': analytic_line,
            'line_date': line_date,
            'work_type_ids':work_type_ids,
            'portal_timesheet':True,
        }
        return request.render("odoo_mobile_timesheet.edit_timesheet", values)

    @http.route(['/my/update_timesheet'], type='http', auth="user", website=True)
    def update_timesheet(self, **kwargs):
        if not (request.env.user.has_group('base.group_user') and request.env.user.has_group('hr_timesheet.group_hr_timesheet_user')) or not kwargs:
            return request.render("odoo_mobile_timesheet.not_allowed")
        valse = {}
        if kwargs.get('project_id'):
            valse.update({'project_id': int(kwargs.get('project_id'))})
        if kwargs.get('task_id'):
            valse.update({'task_id': int(kwargs.get('task_id'))})
        if kwargs.get('quantity'):
            quantity_str = str(kwargs.get('quantity'))
            try:
                date_tt = datetime.strptime(quantity_str,'%H:%M') - datetime.strptime(str('0:0'),'%H:%M')
            except:
                return request.render("odoo_mobile_timesheet.hour_usererror_msg")
            quantity = date_tt.total_seconds()/3600.00
            valse.update({'unit_amount': quantity})
        if kwargs.get('work_type'):
            valse.update({'work_type_id': int(kwargs.get('work_type'))})
        if kwargs.get('start_time'):
            start = datetime.strptime(str(kwargs.get('start_time')),'%H:%M') - datetime.strptime(str('0:0'),'%H:%M')
            start_time = start.total_seconds()/3600.00
            valse.update({'start_time': start_time})
        if kwargs.get('end_time'):
            end = datetime.strptime(str(kwargs.get('end_time')),'%H:%M') - datetime.strptime(str('0:0'),'%H:%M')
            end_time = end.total_seconds()/3600.00
            valse.update({'end_time': end_time})
        if kwargs.get('is_billable'):
            if kwargs.get('is_billable') == 'on':
                valse.update({'is_billable': True})
            else:
                valse.update({'is_billable' : False})
        if kwargs.get('is_paid'):
            if kwargs.get('is_paid') == 'on':
                valse.update({'is_paid': True})
            else:
                valse.update({'is_paid': False})
        if kwargs.get('description'):
            valse.update({'name': kwargs.get('description')})
        if kwargs.get('date'):
            date = datetime.strptime(kwargs.get('date'), "%Y-%m-%d")
            valse.update({'date': date})
        if kwargs.get('line_id'):
            line_id = request.env['account.analytic.line'].browse(int(kwargs.get('line_id')))
            if line_id.is_billable == True and not kwargs.get('is_billable'):
                valse.update({'is_billable' : False})
            if line_id.is_paid == True and not kwargs.get('is_paid'):
                valse.update({'is_paid' : False})
            if line_id:
                line_id.write(valse)
                return request.redirect("/odoo_timesheet_portal_user_employee/select_timesheet?start_date="+str(line_id.date))
        return request.render("odoo_mobile_timesheet.edit_timesheet")

    @http.route(['/my/timesheet/delete/<int:timesheet>'], type='http', auth="user", website=True)
    def delete_timesheet(self, timesheet=None, **kw):
        analytic_line = request.env['account.analytic.line'].browse([timesheet])
        start_date = analytic_line.date
        try:
            analytic_line.unlink()
        except:
            return request.render("odoo_mobile_timesheet.not_allowed")
        return request.redirect("/odoo_timesheet_portal_user_employee/select_timesheet?start_date="+str(start_date))
        
    @http.route(['/odoo_timesheet_portal_user_employee/select_timesheet'], auth='user', website=True)
    def select_timesheet(self, page=1, sortby=None, **kw):
        if not (request.env.user.has_group('base.group_user') and request.env.user.has_group('hr_timesheet.group_hr_timesheet_user')):
            return request.render("odoo_mobile_timesheet.not_allowed")
        if kw.get('start_date'):
            response = super(CustomerPortal, self)
            values = {}
            timesheets_obj = http.request.env['account.analytic.line']
            domain = [
            ('user_id', 'child_of', [request.env.user.id]),
            ]
            # count for pager
            timesheets_count = http.request.env['account.analytic.line'].search_count(domain)
            # pager
            pager = request.website.pager(
                url="/my/timesheets",
                total=timesheets_count,
                page=page,
                step=self._items_per_page
            )
            sortings = {
                'date': {'label': _('Newest'), 'order': 'date desc'},
                'project': {'label': _('Project'), 'order': 'project_id'},
            }
            
            order = sortings.get(sortby, sortings['date'])['order']
            
            # content according to pager and archive selected
            domain += [('date', '=', kw.get('start_date'))]
            timesheets = timesheets_obj.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
            values.update({
                'timesheets': timesheets,
                'page_name': 'timesheets',
                'start_date':kw.get('start_date'),
                'timesheet_date':kw.get('start_date'),
                'sortings' : sortings,
                'sortby': sortby,
                'pager': pager,
                'default_url': '/odoo_timesheet_portal_user_employee/select_timesheet',
                'portal_timesheet':True,
            })
        else:
            response = super(CustomerPortal, self)
            values = {}
            timesheets_obj = http.request.env['account.analytic.line']
            domain = [
                ('user_id', 'child_of', [request.env.user.id]),
                ]
            # count for pager
            timesheets_count = http.request.env['account.analytic.line'].search_count(domain)
            # pager
            pager = request.website.pager(
                url="/odoo_timesheet_portal_user_employee/select_timesheet",
                total=timesheets_count,
                page=page,
                step=self._items_per_page
            )
            sortings = {
                'date': {'label': _('Newest'), 'order': 'date desc'},
                'project': {'label': _('Project'), 'order': 'project_id'},
            }
            if kw.get("search"):
                domain += ['|', ('date', 'ilike', kw.get("search")), ('name', 'ilike', kw.get("search"))]
            order = sortings.get(sortby, sortings['date'])['order']
            
            # content according to pager and archive selected
            timesheets = timesheets_obj.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
            values.update({
                'timesheets': timesheets,
                'page_name': 'timesheets',
                'start_date': fields.Date.today(),
                'sortings' : sortings,
                'sortby': sortby,
                'pager': pager,
                'default_url': '/odoo_timesheet_portal_user_employee/select_timesheet',
                'portal_timesheet':True,
            })
        return request.render("odoo_mobile_timesheet.display_timesheets", values)

