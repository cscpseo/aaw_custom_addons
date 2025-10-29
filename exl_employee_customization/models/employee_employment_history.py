from odoo import models, fields

class EmployeeEmploymentHistory(models.Model):
    _name = 'employee.employment.history'
    _description = 'Employee Employment History'

    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade')
    position = fields.Char(string='Position')
    organization = fields.Char(string='Organization')
    city_id = fields.Char(string='City')  # Using city Many2one as before
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    employment_type = fields.Selection([
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ], string='Employment Type')
    last_salary = fields.Monetary(string='Last Salary', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency')
    reason_of_leaving = fields.Text(string='Reason of Leaving')
