# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from dateutil.relativedelta import relativedelta


class VehicleCost(models.Model):
    _name = 'vehicle.cost'
    _description = 'Cost related to external vehicle'
    _order = 'date desc, vehicle_id asc'

    name = fields.Char(related='vehicle_id.name', string='Name', store=True, readonly=False)
    vehicle_id = fields.Many2one('vehicle', 'Vehicle', required=True, help='Vehicle concerned by this log')
    amount = fields.Float('Total Price')
    cost_type = fields.Selection([
        ('fuel', 'Fuel'),
        ('other', 'Other')
        ], 'Category of the cost', default="other", help='For internal purpose only', required=True)
    parent_id = fields.Many2one('vehicle.cost', 'Parent', help='Parent cost to this current cost')
    cost_ids = fields.One2many('vehicle.cost', 'parent_id', 'Included Services', copy=True)
    odometer_id = fields.Many2one('vehicle.odometer', 'Odometer', help='Odometer measure of the vehicle at the moment of this log')
    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer', string='Odometer Value',
        help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed')
    auto_generated = fields.Boolean('Automatically Generated', readonly=True)
    description = fields.Char("Cost Description")

    @api.model_create_multi
    def create(self, vals_list):
        for data in vals_list:
            # make sure that the data are consistent with values of parent and contract records given
            if 'parent_id' in data and data['parent_id']:
                parent = self.browse(data['parent_id'])
                data['vehicle_id'] = parent.vehicle_id.id
                data['date'] = parent.date
                data['cost_type'] = parent.cost_type
            if 'odometer' in data and not data['odometer']:
                # if received value for odometer is 0, then remove it from the
                # data as it would result to the creation of a
                # odometer log with 0, which is to be avoided
                del data['odometer']
        return super(VehicleCost, self).create(vals_list)

    def _get_odometer(self):
        for record in self:
            if record.odometer_id:
                record.odometer = record.odometer_id.value

    def _set_odometer(self):
        for record in self:
            if not record.odometer:
                raise UserError(_('Emptying the odometer value of a vehicle is not allowed.'))
            odometer = self.env['vehicle.odometer'].create({
                'value': record.odometer,
                'date': record.date or fields.Date.context_today(record),
                'vehicle_id': record.vehicle_id.id
            })
            self.odometer_id = odometer


class VehicleLogFuel(models.Model):
    _name = 'vehicle.log.fuel'
    _description = 'Fuel log for external vehicles'
    _inherits = {'vehicle.cost': 'cost_id'}

    @api.model
    def default_get(self, default_fields):
        res = super(VehicleLogFuel, self).default_get(default_fields)
        res.update({
            'date': fields.Date.context_today(self),
            'cost_type': 'fuel'
        })
        return res

    liter = fields.Float()
    price_per_liter = fields.Float()
    purchaser_id = fields.Char('Purchaser')
    inv_ref = fields.Char('Invoice Reference', size=64)
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier','=',True)]")
    notes = fields.Text()
    cost_id = fields.Many2one('vehicle.cost', 'Cost', required=True, ondelete='cascade')
    # we need to keep this field as a related with store=True because the graph view doesn't support
    # (1) to address fields from inherited table
    # (2) fields that aren't stored in database
    cost_amount = fields.Float(related='cost_id.amount', string='Amount', store=True, readonly=False)

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.purchaser_id = self.vehicle_id.driver

    @api.onchange('liter', 'price_per_liter', 'amount')
    def _onchange_liter_price_amount(self):
        # need to cast in float because the value receveid from web client maybe an integer (Javascript and JSON do not
        # make any difference between 3.0 and 3). This cause a problem if you encode, for example, 2 liters at 1.5 per
        # liter => total is computed as 3.0, then trigger an onchange that recomputes price_per_liter as 3/2=1 (instead
        # of 3.0/2=1.5)
        # If there is no change in the result, we return an empty dict to prevent an infinite loop due to the 3 intertwine
        # onchange. And in order to verify that there is no change in the result, we have to limit the precision of the
        # computation to 2 decimal
        liter = float(self.liter)
        price_per_liter = float(self.price_per_liter)
        amount = float(self.amount)
        if liter > 0 and price_per_liter > 0 and round(liter * price_per_liter, 2) != amount:
            self.amount = round(liter * price_per_liter, 2)
        elif amount > 0 and liter > 0 and round(amount / liter, 2) != price_per_liter:
            self.price_per_liter = round(amount / liter, 2)
        elif amount > 0 and price_per_liter > 0 and round(amount / price_per_liter, 2) != liter:
            self.liter = round(amount / price_per_liter, 2)


