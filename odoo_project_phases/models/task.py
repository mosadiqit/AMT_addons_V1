# -*- coding: utf-8 -*-

from odoo import fields, models


class Task(models.Model):
    _inherit = "project.task"

    project_phase_id = fields.Many2one(
        'project.phase',
        string="Project Phase",
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
