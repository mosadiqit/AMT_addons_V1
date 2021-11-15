# -*- coding: utf-8 -*-

from odoo import models, api, fields


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Types of external vehicles'

    name = fields.Char(string='Type')
