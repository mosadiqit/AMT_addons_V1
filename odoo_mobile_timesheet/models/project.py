# -*- coding: utf-8 -*-

from odoo import models, fields

class Project(models.Model):
    _inherit = 'project.project'
    
    is_close = fields.Boolean(
        string='Hide Project',
    )
