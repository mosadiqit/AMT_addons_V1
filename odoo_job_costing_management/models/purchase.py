# -*- coding: utf-8 -*-

from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    picking_id = fields.Many2one(
        'stock.picking',
        string='Stock Picking',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

