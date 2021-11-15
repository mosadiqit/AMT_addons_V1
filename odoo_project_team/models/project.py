# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'
    
    @api.onchange('project_team_id')
    def onchange_project_team(self):
        for rec in self:
            rec.project_engineer_id = rec.project_team_id.project_engineer_id.id
            rec.user_id = rec.project_team_id.project_manager_id.id
            rec.store_officer_ids = rec.project_team_id.store_officer_ids.ids
            rec.security_guard_ids = rec.project_team_id.security_guard_ids.ids
            rec.team_member_ids = rec.project_team_id.team_member_ids.ids
        
    
    project_team_id = fields.Many2one(
        'project.team.custom',
        string='Project Team',
        copy=False
    )
    project_engineer_id = fields.Many2one(
        'res.users',
        string='Site Engineer / Supervisor',
        copy=False
    )
    store_officer_ids = fields.Many2many(
        'res.users',
        'team_store_officer_res_user',
        string='Store Officers',
        copy=False
    )
    security_guard_ids = fields.Many2many(
        'res.users',
        'team_security_guard_res_user',
        string='Security Guards',
        copy=False
    )
    team_member_ids = fields.Many2many(
        'res.users',
        'team_project_team_res_user',
        string='Team Members',
        copy=False
    )

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            self.project_team_id = self.project_id.project_team_id.id
            self.project_engineer_id = self.project_id.project_team_id.project_engineer_id.id
            self.store_officer_ids = self.project_id.project_team_id.store_officer_ids.ids
            self.security_guard_ids = self.project_id.project_team_id.security_guard_ids.ids
            self.team_member_ids = self.project_id.project_team_id.team_member_ids.ids
        return super(ProjectTask, self)._onchange_project()
    
    project_team_id = fields.Many2one(
        'project.team.custom',
        string='Project Team',
        copy=False
    )
    project_engineer_id = fields.Many2one(
        'res.users',
        string='Site Engineer / Supervisor',
        copy=False
    )
    store_officer_ids = fields.Many2many(
        'res.users',
        'task_store_officer_res_user',
        string='Store Officers',
        copy=False
    )
    security_guard_ids = fields.Many2many(
        'res.users',
        'task_security_guard_res_user',
        string='Security Guards',
        copy=False
    )
    team_member_ids = fields.Many2many(
        'res.users',
        'task_project_team_res_user',
        string='Team Members',
        copy=False
    )