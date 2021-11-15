# -*- coding: utf-8 -*-

from odoo import fields, models


class HrTimesheetConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    module_project_timesheet_synchro = fields.Boolean(string="Timesheet app for Chrome/Android/iOS")
    timesheet_range = fields.Selection(related='company_id.timesheet_range', string="Timesheet range *")
