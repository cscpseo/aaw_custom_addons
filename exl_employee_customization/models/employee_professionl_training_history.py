from odoo import models, fields

class EmployeeProfessionalTrainingHistory(models.Model):
    _name = 'employee.professional.training.history'
    _description = 'Employee Professional Training History'

    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade')
    training_title = fields.Char(string='Training Title')
    institute = fields.Char(string='Institute')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    city = fields.Char(string='City')