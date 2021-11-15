# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    timesheet_range = fields.Selection(
        [('week', 'Week'), ('month', 'Month')],
        default='week', string='Timesheet range', 
        help="Periodicity on which you validate your timesheets."
    )
