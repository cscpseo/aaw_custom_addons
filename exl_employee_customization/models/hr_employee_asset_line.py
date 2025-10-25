from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeAssetLine(models.Model):
    _name = 'employee.asset.line'
    _description = 'Employee Asset Line'

    sequence = fields.Integer(
        string="Sequence",
        help="Gives the sequence order when displaying a list of sale quote lines.",
        default=10)
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='cascade')
    line_type = fields.Selection([
        ('asset', 'Asset'),
        ('note', 'Note'),
    ], string="Line Type", default='asset')
    asset_name = fields.Char(string="Asset Name / Particulars", required=True)
    qty = fields.Integer(string="QTY", default=1)
    company_made_by = fields.Char(string="Company Made By")
    model_gen = fields.Char(string="Model / Gen")
    capacity = fields.Char(string="Capacity")
    remarks = fields.Char(string="Remarks")

    imei_1 = fields.Char(string="IMEI 1")
    imei_2 = fields.Char(string="IMEI 2")
    sim_number = fields.Char(string="SIM Number")

    @api.constrains('qty')
    def _check_positive_qty_sim(self):
        for record in self:
            if record.qty <= 0:
                raise ValidationError("Quantity (QTY) must be greater than 0.")

    @api.constrains('sim_number')
    def _check_sim_number_format(self):
        for record in self:
            if record.sim_number:
                sim = record.sim_number
                if not sim.isdigit():
                    raise ValidationError("SIM Number must contain only digits.")
                if not sim.startswith('03'):
                    raise ValidationError(
                        "SIM Number must start with 03")
                if len(sim) != 11:
                    raise ValidationError("SIM Number must be exactly 11 digits.")
