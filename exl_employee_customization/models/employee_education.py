from odoo import models, fields

class EmployeeEducation(models.Model):
    _name = 'employee.education'
    _description = 'Employee Education Details'

    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade')
    degree_id = fields.Many2one('employee.education.degree', string='Degree / Diploma')
    institute = fields.Char(string='Institute')
    city = fields.Char(string='City')
    specialization = fields.Char(string='Specialization')
    year = fields.Char(string='Year of Passing')
    cgpa = fields.Char(string='CGPA / Division')
    honours = fields.Char(string='Honours / Distinction')