# -*- coding: utf-8 -*-

from odoo import models, fields

class JobCosting(models.Model):
    _inherit = 'job.costing'
    
    project_team_id = fields.Many2one(
        'project.team.custom',
        string='Project Team',
        copy=False
    )
    tag_ids = fields.Many2many(
        'costsheet.tag',
        string='Tags',
        copy=False
    )
  