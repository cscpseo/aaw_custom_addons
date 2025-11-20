from odoo import models, fields, api
from datetime import datetime, date, timedelta

class HrAttendanceSummaryWizard(models.TransientModel):
    _name = 'hr.attendance.summary.wizard'
    _description = 'Attendance Summary Wizard'

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

        SummaryModel = self.env['hr.attendance.summary']

        # Filter summaries
        domain = [('date_from', '=', start), ('date_to', '=', end)]

        if self.company_id:
            domain.append(('employee_id.company_id', '=', self.company_id.id))

        if self.department_id:
            domain.append(('employee_id.department_id', '=', self.department_id.id))

        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))

        summaries = SummaryModel.search(domain)

        if not summaries:
            self.action_compute_and_save()
            summaries = SummaryModel.search(domain)

        return self.env.ref(
            'tis_hr_biometric_attendance.attendance_summary_xlsx_report'
        ).report_action(summaries)

    # ---------------------------------------------------------
    # COMPUTE ATTENDANCE SUMMARY
    # ---------------------------------------------------------
    def action_compute_and_save(self):
        self.ensure_one()

        Employee = self.env['hr.employee']
        Attendance = self.env['hr.attendance']
        TimeOff = self.env['hr.leave']

        start = self.date_from
        end = self.date_to

        if not Attendance.search([]):
            raise models.ValidationError("No attendance found!")

        if not start or not end or start > end:
            raise models.ValidationError("Please set a valid date range")

        # Remove old summaries
        self.env['hr.attendance.summary'].search([]).unlink()

        # Filter employees
        emp_domain = []
        if self.company_id:
            emp_domain.append(('company_id', '=', self.company_id.id))
        if self.department_id:
            emp_domain.append(('department_id', '=', self.department_id.id))
        if self.employee_id:
            emp_domain.append(('id', '=', self.employee_id.id))

        employees = Employee.search(emp_domain)

        SummaryModel = self.env['hr.attendance.summary']

        # ---------------------------------------------------------
        # MAIN LOOP — PER EMPLOYEE PER DAY
        # ---------------------------------------------------------
        for emp in employees:

            total_days = present_days = leave_days = absent_days = late_count = 0
            current = start

            while current <= end:

                # Skip Sundays only
                if current.weekday() == 6:
                    current += timedelta(days=1)
                    continue

                total_days += 1

                day_start = datetime.combine(current, datetime.min.time())
                day_end = datetime.combine(current, datetime.max.time())

                # ---------------------------------------------------------
                # CHECK LEAVE (CORRECT FIELDS)
                # ---------------------------------------------------------
                has_leave = TimeOff.search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'validate'),
                    ('date_from', '<=', day_end),
                    ('date_to', '>=', day_start),
                ], limit=1)

                if has_leave:
                    leave_days += 1
                    current += timedelta(days=1)
                    continue

                # ---------------------------------------------------------
                # CHECK ATTENDANCE (check-in OR check-out)
                # ---------------------------------------------------------
                attendance = Attendance.search([
                    ('employee_id', '=', emp.id),
                    '|',
                    '&', ('check_in', '>=', day_start), ('check_in', '<=', day_end),
                    '&', ('check_out', '>=', day_start), ('check_out', '<=', day_end),
                ], limit=1)

                if attendance:
                    present_days += 1
                    if attendance.is_late:
                        late_count += 1
                else:
                    absent_days += 1

                current += timedelta(days=1)

            # ---------------------------------------------------------
            # CREATE SUMMARY RECORD
            # ---------------------------------------------------------
            SummaryModel.create({
                'employee_id': emp.id,
                'date_from': start,
                'date_to': end,
                'total_days': total_days,
                'present_days': present_days,
                'leave_days': leave_days,
                'absent_days': absent_days,
                'late_count': late_count,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Summaries',
            'res_model': 'hr.attendance.summary',
            'view_mode': 'list,form',
            'target': 'current',
        }