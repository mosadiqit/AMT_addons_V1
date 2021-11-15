# -*- coding: utf-8 -*-

import time
from odoo import api, models

class ReportTimesheet(models.AbstractModel):
    _name = 'report.odoo_timesheet_sheet.hr_timesheet_report_id'
    
    def get_total_hours(self, obj):
        totalhours = 0
        for record in obj.timesheet_ids:
            totalhours += record.unit_amount
        return totalhours
    
    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids':docids,
            'doc_model': 'hr_timesheet_sheet.sheet',
            'data': data,
            'docs': self.env['hr_timesheet_sheet.sheet'].browse(docids),
            'get_total_hours': self.get_total_hours,
        }
