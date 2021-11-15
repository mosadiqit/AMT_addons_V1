# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression

class Color(models.Model):
    _name = 'color'
    name = fields.Char('Name')


class partner(models.Model):
    _inherit ='res.partner'

    vehicle_ids = fields.One2many('vehicle', 'owner_id')

    @api.multi
    @api.depends('vehicle_ids')
    def _vehicle_count(self):
        for rec in self:
            rec.vehicle_count = len(rec.vehicle_ids)

    vehicle_count = fields.Integer(
        string='Vehicles',
        store=True,
        compute='_vehicle_count',
     )

    @api.multi
    def show_vehicle(self):
        for rec in self:
            res = self.env.ref('vehicle.fleet_vehicle_action')
            res = res.read()[0]
            res['domain'] = str([('id', 'in', rec.vehicle_ids.ids)])
        return res

    # is_insurance = fields.Boolean('Insurance')


class FleetVehicle(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'vehicle'
    _description = 'Vehicle'
    _order = 'license_plate asc'

    name = fields.Char(compute="_compute_vehicle_name", store=True)
    vehicle_type = fields.Many2one('vehicle.type', string='Vehicle Type')
    is_insured = fields.Boolean('is insured ?')
    # insurance_company = fields.Many2one('res.partner',string='Insurance Company')
    insurance_company = fields.Char(string='Insurance Company')
    active = fields.Boolean('Active', default=True, track_visibility="onchange")
    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer', string='Odometer')
    odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
        ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True)

    # owner_id = fields.Many2one('res.partner', string='Owner', required=False)
    owner_id = fields.Many2one('res.partner', string='Owner', domain=[('supplier', '=', True)])
    driver = fields.Char(string='Driver')

    company_id = fields.Many2one('res.company', 'Company')
    license_plate = fields.Char(track_visibility="onchange",
        help='License plate number of the vehicle (i = plate number for a car)')
    vin_sn = fields.Char('Chassis Number', help='Unique number written on the vehicle motor (VIN/SN number)', copy=False)
    driver_id = fields.Many2one('res.partner', 'Driver', track_visibility="onchange", help='Driver of the vehicle', copy=False)
    model_id = fields.Many2one('vehicle.model', 'Model',
        track_visibility="onchange", required=True, help='Model of the vehicle')
    brand_id = fields.Many2one('vehicle.model.brand', 'Brand', related="model_id.brand_id", store=True, readonly=False)
    acquisition_date = fields.Date('Immatriculation Date', required=False,
        default=fields.Date.today, help='Date when the vehicle has been immatriculated')
    first_contract_date = fields.Date(string="First Contract Date", default=fields.Date.today)
    color = fields.Many2one('color',help='Color of the vehicle')
    location = fields.Char(help='Location of the vehicle (garage, ...)')
    seats = fields.Integer('Seats Number', help='Number of seats of the vehicle')
    model_year = fields.Char('Model Year',help='Year of the model')
    doors = fields.Integer('Doors Number', help='Number of doors of the vehicle', default=5)
    tag_ids = fields.Many2many('vehicle.tag', 'vehicle_vehicle_tag_rel', 'vehicle_tag_id', 'tag_id', 'Tags', copy=False)
    transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission', help='Transmission Used by the vehicle')
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
        ], 'Fuel Type', help='Fuel Used by the vehicle')
    fuel_logs_count = fields.Integer(compute="_compute_count_all", string='Fuel Log Count')
    cost_count = fields.Integer(compute="_compute_count_all", string="Costs")
    horsepower = fields.Integer()
    horsepower_tax = fields.Float('Horsepower Taxation')
    power = fields.Integer('Power', help='Power in kW of the vehicle')
    co2 = fields.Float('CO2 Emissions', help='CO2 emissions of the vehicle')
    image = fields.Binary(related='model_id.image', string="Logo", readonly=False)
    image_medium = fields.Binary(related='model_id.image_medium', string="Logo (medium)", readonly=False)
    image_small = fields.Binary(related='model_id.image_small', string="Logo (small)", readonly=False)


    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = record.model_id.brand_id.name + '/' + record.model_id.name + '/' + (record.license_plate or _('No Plate'))

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        domain = expression.AND([domain, [('name', operator, name)]])
        # we don't want to override the domain's filter on driver_id if present
        if not any(['driver_id' in element for element in domain]):
            partner_ids = self.env['res.partner']._search([('name', operator, name)], access_rights_uid=name_get_uid)
            if partner_ids:
                domain = expression.OR([domain, ['|', ('driver_id', 'in', partner_ids), ('driver_id', '=', False)]])
        rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(rec).name_get()

    def _compute_count_all(self):
        LogFuel = self.env['vehicle.log.fuel']
        Cost = self.env['vehicle.cost']
        for record in self:
            record.fuel_logs_count = LogFuel.search_count([('vehicle_id', '=', record.id)])
            record.cost_count = Cost.search_count([('vehicle_id', '=', record.id), ('parent_id', '=', False)])

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('vehicle', xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False

    @api.multi
    def act_show_log_cost(self):
        """ This opens log view to view and add new log for this vehicle, groupby default to only show effective costs
            @return: the costs log view
        """
        self.ensure_one()
        copy_context = dict(self.env.context)
        copy_context.pop('group_by', None)
        res = self.env['ir.actions.act_window'].for_xml_id('vehicle', 'vehicle_costs_action')
        res.update(
            context=dict(copy_context, default_vehicle_id=self.id, search_default_parent_false=True),
            domain=[('vehicle_id', '=', self.id)]
        )
        return res

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'driver_id' in init_values:
            return 'vehicle.mt_fleet_driver_updated'
        return super(FleetVehicle, self)._track_subtype(init_values)

    def open_assignation_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignation Logs',
            'view_mode': 'tree',
            'res_model': 'vehicle.vehicle.assignation.log',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_driver_id': self.driver_id.id, 'default_vehicle_id': self.id}
        }

    def _get_odometer(self):
        VehicleOdometer = self.env['vehicle.odometer']
        for record in self:
            vehicle_odometer = VehicleOdometer.search([('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        for record in self:
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date, 'vehicle_id': record.id}
                self.env['vehicle.odometer'].create(data)


class FleetVehicleTag(models.Model):
    _name = 'vehicle.tag'
    _description = 'Vehicle Tag'

    name = fields.Char(required=True, translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists !")]


class VehicleOdometer(models.Model):
    _name = 'vehicle.odometer'
    _description = 'Odometer log for external vehicle'
    _order = 'date desc, id desc'

    name = fields.Char(compute='_compute_vehicle_log_name', store=True)
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Float('Odometer Value', group_operator="max")
    vehicle_id = fields.Many2one('vehicle', 'Vehicle', required=True)

    @api.depends('vehicle_id', 'date')
    def _compute_vehicle_log_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name
