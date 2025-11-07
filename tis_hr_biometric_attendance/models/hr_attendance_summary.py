from odoo import models, fields, api

class HrAttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _description = 'Attendance Summary (persistent)'
    _order = 'date_from desc, employee_id'

    employee_id  = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    date_from    = fields.Date(string='Start Date', required=True)
    date_to      = fields.Date(string='End Date',   required=True)
    total_days   = fields.Integer(string='Total Working Days', readonly=True)
    present_days = fields.Integer(string='Present Days',       readonly=True)
    leave_days   = fields.Integer(string='Leave Days',         readonly=True)
    absent_days  = fields.Integer(string='Absent Days',        readonly=True)
    summary_date = fields.Date(string='Generated On', default=fields.Date.context_today, readonly=True)

    @api.model
    def create(self, vals):
        # you could add constraints / checking here
        return super(HrAttendanceSummary, self).create(vals)
