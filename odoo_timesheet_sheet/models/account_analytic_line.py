# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import datetime
from odoo import api, fields, models, modules, tools, SUPERUSER_ID, _

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    sheet_id_computed = fields.Many2one(
        'hr_timesheet_sheet.sheet', 
        string='Sheet', 
        compute='_compute_sheet', 
        index=True, 
        ondelete='cascade',
        search='_search_sheet'
    )
    sheet_id = fields.Many2one(
        'hr_timesheet_sheet.sheet', 
        compute='_compute_sheet', 
        string='Sheet', 
        store=True
    )

    @api.depends('date', 'user_id', 'project_id', 
                 'sheet_id_computed.date_to', 
                 'sheet_id_computed.date_from', 
                 'sheet_id_computed.employee_id')
    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet
        """
        for ts_line in self:
            if not ts_line.project_id:
                continue
            sheets = self.env['hr_timesheet_sheet.sheet'].search(
                [('date_to', '>=', ts_line.date), ('date_from', '<=', ts_line.date),
                 ('employee_id.user_id.id', '=', ts_line.user_id.id),
                 ('state', 'in', ['draft', 'new'])])
            if sheets:
                # [0] because only one sheet possible for an employee between 2 dates
                ts_line.sheet_id_computed = sheets[0]
                ts_line.sheet_id = sheets[0]

    def _search_sheet(self, operator, value):
        assert operator == 'in'
        ids = []
        for ts in self.env['hr_timesheet_sheet.sheet'].browse(value):
            self._cr.execute("""
                    SELECT l.id
                        FROM account_analytic_line l
                    WHERE %(date_to)s >= l.date
                        AND %(date_from)s <= l.date
                        AND %(user_id)s = l.user_id
                    GROUP BY l.id""", {'date_from': ts.date_from,
                                       'date_to': ts.date_to,
                                       'user_id': ts.employee_id.user_id.id, })
            ids.extend([row[0] for row in self._cr.fetchall()])
        return [('id', 'in', ids)]

    @api.multi
    def write(self, values):
        ctx = self._context.copy()
        if not ctx.get('skip_warning', False):
            self._check_state()
        return super(AccountAnalyticLine, self).write(values)

    @api.multi
    def unlink(self):
        self._check_state()
        return super(AccountAnalyticLine, self).unlink()

    def _check_state(self):
        for line in self:
            if line.sheet_id and line.sheet_id.state not in ('draft', 'new'):
                raise UserError(_('You cannot modify an entry in a confirmed timesheet.'))
        return True

    @api.model
    def create(self, vals):
        res = super(AccountAnalyticLine, self).create(vals)
        if type(vals['date']) == type('str'):
            vals_date = datetime.strptime(vals['date'], tools.DEFAULT_SERVER_DATE_FORMAT).date()
        else:
            vals_date = datetime.strptime(vals['date'].strftime(tools.DEFAULT_SERVER_DATE_FORMAT), tools.DEFAULT_SERVER_DATE_FORMAT).date()
        #vals_date = datetime.strptime(vals['date'], tools.DEFAULT_SERVER_DATE_FORMAT).date()
        if vals.get('sheet_id'):
            hr_timesheet_obj = self.env['hr_timesheet_sheet.sheet'].browse(vals.get('sheet_id'))
            if not vals_date >= hr_timesheet_obj.date_from or not vals_date <= hr_timesheet_obj.date_to:
                raise UserError(_('Invalid timesheet date.'))
        return res
