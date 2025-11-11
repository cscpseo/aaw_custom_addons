from odoo import models, fields, api
from datetime import datetime, date, timedelta

class HrAttendanceSummaryWizard(models.TransientModel):
    _name = 'hr.attendance.summary.wizard'
    _description = 'Attendance Summary Wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date",   required=True)
    company_id = fields.Many2one('res.company', string="Company")
    department_id = fields.Many2one('hr.department', string="Department", domain="[('company_id', '=', company_id)]")

    def action_export_xlsx(self):
        self.ensure_one()

        start = self.date_from
        end = self.date_to

        if not start or not end or start > end:
            raise models.ValidationError("Please set a valid date range")

        SummaryModel = self.env['hr.attendance.summary']

        # Fetch existing summaries
        domain = [('date_from', '=', start), ('date_to', '=', end)]
        if self.department_id:
            domain.append(('employee_id.department_id', '=', self.department_id.id))
        summaries = SummaryModel.search(domain)

        # If no summaries, compute and create them automatically
        if not summaries:
            self.action_compute_and_save()
            summaries = SummaryModel.search(domain)

        # Finally, generate XLSX
        return self.env.ref('tis_hr_biometric_attendance.attendance_summary_xlsx_report').report_action(summaries)

    def action_compute_and_save(self):
        self.ensure_one()
        Employee = self.env['hr.employee']
        Attendance = self.env['hr.attendance']
        TimeOff = self.env['hr.leave']
        PublicHoliday = self.env['resource.calendar.leaves']

        start = fields.Date.from_string(self.date_from)
        end = fields.Date.from_string(self.date_to)

        if not Attendance.search([]):
            raise models.ValidationError("No Attendance Found")

        if not start or not end or start > end:
            raise models.ValidationError("Please set a valid date range")

        # Delete old summaries
        self.env['hr.attendance.summary'].search([]).unlink()

        # Get employees
        domain_emp = []
        if self.department_id:
            domain_emp = [('department_id', '=', self.department_id.id)]
        employees = Employee.search(domain_emp)

        # Prepare list of holiday dates
        holidays = set()
        holiday_records = PublicHoliday.search([('date_from', '<=', end), ('date_to', '>=', start)])
        for leave in holiday_records:
            leave_start = max(fields.Date.from_string(leave.date_from), start)
            leave_end = min(fields.Date.from_string(leave.date_to), end)
            delta = (leave_end - leave_start).days
            for i in range(delta + 1):
                holidays.add(leave_start + timedelta(days=i))

        SummaryModel = self.env['hr.attendance.summary']

        for emp in employees:
            total_days = present_days = leave_days = absent_days = late_count = 0
            current = start

            while current <= end:
                # Skip Sundays
                if current.weekday() == 6:
                    current += timedelta(days=1)
                    continue
                # Skip public holidays
                if current in holidays:
                    current += timedelta(days=1)
                    continue

                total_days += 1  # counting this as working day

                # Check leave
                has_leave = TimeOff.search([
                    ('employee_id', '=', emp.id),
                    ('request_date_from', '<=', current),
                    ('request_date_to', '>=', current),
                    ('state', '=', 'validate')
                ], limit=1)

                if has_leave:
                    leave_days += 1
                else:
                    # Check attendance
                    att = Attendance.search([
                        ('employee_id', '=', emp.id),
                        ('check_in', '>=', datetime.combine(current, datetime.min.time())),
                        ('check_in', '<=', datetime.combine(current, datetime.max.time()))
                    ], limit=1)

                    if att:
                        present_days += 1
                        if att.is_late:  # ✅ Count lateness
                            late_count += 1
                    else:
                        absent_days += 1

                current += timedelta(days=1)

            # Create summary record
            SummaryModel.create({
                'employee_id': emp.id,
                'date_from': start,
                'date_to': end,
                'total_days': total_days,
                'present_days': present_days,
                'leave_days': leave_days,
                'absent_days': absent_days,
                'late_count': late_count,  # ✅ New field
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Summaries',
            'res_model': 'hr.attendance.summary',
            'view_mode': 'list,form',
            'target': 'current',
        }