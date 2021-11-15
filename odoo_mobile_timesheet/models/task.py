# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    is_close = fields.Boolean(
        string='Is Closed',
    )
