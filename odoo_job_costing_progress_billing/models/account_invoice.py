# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    job_cost_id = fields.Many2one(
        'job.costing',
        readonly=True,
        string="Job Cost Sheet",
    )
