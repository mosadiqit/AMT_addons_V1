# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    start_time = fields.Float(
        string="Start Time",
    )
    end_time = fields.Float(
        string="End Time",
    )
    work_type_id = fields.Many2one(
        'timesheet.work.type',
        string="Work Type",
    )
    is_billable = fields.Boolean(
        string="Is Billable",
    )
    is_paid = fields.Boolean(
        string="Is Paid",
    )
#    payment_status = fields.Selection(
#        selection=[
#                   ('unpaid', 'UnPaid'),
#                   ('paid', 'Paid'),
#        ],
#        default="unpaid",
#        string="Payment Status",
#    )
