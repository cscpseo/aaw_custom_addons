from odoo import models, fields

class EmployeeEducationDegree(models.Model):
    _name = 'employee.education.degree'
    _description = 'Education Degree / Diploma'

    name = fields.Char(string='Degree / Diploma', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)