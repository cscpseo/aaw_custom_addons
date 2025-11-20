from odoo import models, fields, api
from datetime import datetime, date, timedelta

class HrAttendanceDetailedSummaryWizard(models.TransientModel):
    _name = 'hr.attendance.detailed.summary.wizard'
    _description = 'Attendance Detailed Summary Wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date",   required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)
    department_id = fields.Many2one('hr.department', string="Department", domain="[('company_id', '=', company_id)]")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        domain="[('department_id', '=', department_id)]"
    )

    def action_export_xlsx(self):
        self.ensure_one()

        start = self.date_from
        end = self.date_to

        if not start or not end or start > end:
            raise models.ValidationError("Please set a valid date range")

        Attendance = self.env['hr.attendance']

        # ------------------------------
        # BUILD DOMAIN FROM WIZARD FILTERS
        # ------------------------------
        domain = [
            ('check_in', '>=', datetime.combine(start, datetime.min.time())),
            ('check_in', '<=', datetime.combine(end, datetime.max.time())),
        ]

        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))

        if self.department_id:
            domain.append(('employee_id.department_id', '=', self.department_id.id))

        if self.company_id:
            domain.append(('employee_id.company_id', '=', self.company_id.id))

        # FETCH FILTERED ATTENDANCE
        attendances = Attendance.search(domain, order="employee_id, check_in")

        if not attendances:
            raise models.ValidationError("No attendance found in this date range.")

        # CALL XLSX REPORT USING ATTENDANCE RECORDS
        return self.env.ref(
            'tis_hr_biometric_attendance.attendance_detailed_summary_xlsx_report'
        ).report_action(attendances)