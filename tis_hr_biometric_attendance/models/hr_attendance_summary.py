from odoo import models, fields, api

class HrAttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _description = 'Attendance Summary (persistent)'
    _order = 'date_from desc, employee_id'

    employee_id  = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    date_from    = fields.Date(string='Start Date', required=True)
    date_to      = fields.Date(string='End Date',   required=True)
    total_days   = fields.Integer(string='Total Working Days', readonly=True)
    present_days = fields.Integer(string='Present Days')
    leave_days   = fields.Integer(string='Leave Days')
    absent_days  = fields.Integer(string='Absent Days')
    late_count   = fields.Integer(string='Late Count')
    summary_date = fields.Date(string='Generated On', default=fields.Date.context_today, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="employee_id.company_id")
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, related="employee_id.department_id")

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_late_count(self):
        """Count late attendances for the employee between date_from and date_to."""
        Attendance = self.env['hr.attendance']
        for summary in self:
            if not summary.employee_id or not summary.date_from or not summary.date_to:
                summary.late_count = 0
                continue

            # Count attendance records where employee is late in the given date range
            summary.late_count = Attendance.search_count([
                ('employee_id', '=', summary.employee_id.id),
                ('check_in', '>=', summary.date_from),
                ('check_in', '<=', summary.date_to),
                ('is_late', '=', True),
            ])

    @api.model
    def create(self, vals):
        # you could add constraints / checking here
        return super(HrAttendanceSummary, self).create(vals)
