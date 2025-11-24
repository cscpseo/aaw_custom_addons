# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from datetime import datetime, time

from odoo import models, fields
import pytz


class AttendanceWizard(models.TransientModel):
    _name = 'attendance.calc.wizard'
    _description = 'attendance calc wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)

    def calculate_attendance(self):
        tz = pytz.timezone('Asia/Karachi')  # Adjust to your timezone
        minimal_attendance = self.env['ir.config_parameter'].sudo().get_param(
            'tis_hr_biometric_attendance.minimal_attendance'
        )
        hr_attendance = self.env['hr.attendance']
        now = datetime.now(pytz.utc)
        today_str = now.strftime("%Y-%m-%d %H:%M:%S")

        domain = [
            ('punching_time', '>=', self.date_from),
            ('punching_time', '<=', self.date_to),
            ('is_calculated', '=', False)
        ]
        attendance_logs = self.env['attendance.log'].search(domain)
        hr_attendance.sudo().search([]).unlink()
        for log in attendance_logs:
            punch_utc = log.punching_time
            # Convert UTC → local (Karachi)
            punch_local = pytz.utc.localize(punch_utc).astimezone(tz)
            punch_date = punch_local.date()
            employee_id = log.employee_id.id

            if minimal_attendance:
                attendance = hr_attendance.search([
                    ('employee_id', '=', employee_id),
                    ('punch_date', '=', punch_date)
                ], limit=1)

                if attendance:
                    attendance.write({'check_out': log.punching_time})
                else:
                    last_open = hr_attendance.search([
                        ('employee_id', '=', employee_id),
                        ('check_out', '=', False)
                    ], order='check_in desc', limit=1)

                    if last_open:
                        open_date = last_open.check_in.date()
                        checkout_local = datetime.combine(open_date, time(23, 59, 59))
                        checkout_utc = tz.localize(checkout_local).astimezone(pytz.utc).replace(tzinfo=None)
                        last_open.write({'check_out': checkout_utc})

                    hr_attendance.create({
                        'employee_id': employee_id,
                        'check_in': log.punching_time,
                        'punch_date': punch_date
                    })

                # Ensure same-day auto-checkout is set at *local* 23:59:59
                att_for_day = hr_attendance.search([
                    ('employee_id', '=', employee_id),
                    ('punch_date', '=', punch_date)
                ], limit=1)
                if att_for_day and not att_for_day.check_out:
                    checkout_local = datetime.combine(punch_date, time(23, 59, 59))
                    checkout_utc = tz.localize(checkout_local).astimezone(pytz.utc).replace(tzinfo=None)
                    att_for_day.write({'check_out': checkout_utc})

            # Mark as processed
            log.is_calculated = True

    def check_in_check_out(self, emp_id, time):
        attendances = self.env['hr.attendance'].search([('employee_id', '=', emp_id), ('check_out', '=', False)])
        if attendances:
            return attendances.id
