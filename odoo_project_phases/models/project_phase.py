# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectPhase(models.Model):
    _name = 'project.phase'
    _description = 'Project Phase'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    #_order= 'id desc'
    _order = 'sequence, id'

    name = fields.Char(
        string="Name",
        required=True,
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        required=True,
    )
    start_date = fields.Date(
        string="Start Date",
        default=fields.Date.today(),
        required=True,
    )
    end_date = fields.Date(
        string="End Date",
        default=fields.Date.today(),
    )
    internal_note = fields.Text(
        string="Internal Note",
    )
    user_id = fields.Many2one('res.users',
        default=lambda self: self.env.user,
        string='Responsible User',
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.user.company_id,
        string='Company',
        readonly=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=1,
    )

    @api.multi
    def show_task(self):
        self.ensure_one()
        res = self.env.ref('project.action_view_task')
        res = res.read()[0]
        res['domain'] = str([('project_phase_id', '=', self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
