from odoo import models, fields

class EmployeeReference(models.Model):
    _name = 'employee.reference'
    _description = 'Employee Reference Details'

    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade')

    name = fields.Char(string='Name', required=True)
    organization = fields.Char(string='Organization')
    designation = fields.Char(string='Designation')
    mobile_no = fields.Char(string='Mobile No')
    email = fields.Char(string='Email')