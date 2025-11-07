# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from datetime import datetime, time

from odoo import models
import pytz


class AttendanceWizard(models.TransientModel):
    _name = 'attendance.calc.wizard'
    _description = 'attendance calc wizard'

    # def calculate_attendance(self):
    #     minimal_attendance = self.env['ir.config_parameter'].sudo().get_param(
    #         'tis_hr_biometric_attendance.minimal_attendance')
    #     hr_attendance = self.env['hr.attendance']
    #     # Current datetime in server timezone
    #     now = datetime.now()
    #     today_str = now.strftime("%Y-%m-%d %H:%M:%S")
    #     domain = [
    #         ('punching_time', '<=', today_str),
    #         ('is_calculated', '=', False)
    #     ]
    #     attendance_logs = self.env['attendance.log'].search(domain)
    #     for log in attendance_logs:
    #         # Use date portion of punching_time (may need timezone adjustment if stored UTC)
    #         punch_date = log.punching_time.date()
    #         employee_id = log.employee_id.id
    #
    #         if minimal_attendance:
    #             # Try to find an existing hr.attendance for this employee and date
    #             attendance = hr_attendance.search([
    #                 ('employee_id', '=', employee_id),
    #                 ('punch_date', '=', punch_date)
    #             ], limit=1)
    #             if attendance:
    #                 # If attendance exists, set its check_out to this log's time
    #                 attendance.write({'check_out': log.punching_time})
    #             else:
    #                 # Attendance for this date does not exist
    #                 # Check if there is a previous open attendance (no check_out)
    #                 last_open = hr_attendance.search([
    #                     ('employee_id', '=', employee_id),
    #                     ('check_out', '=', False)
    #                 ], order='check_in desc', limit=1)
    #                 if last_open:
    #                     # Set its check_out at 23:59:59 of its check_in date
    #                     open_date = last_open.check_in.date()
    #                     checkout_time = last_open.check_in.replace(
    #                         hour=23, minute=59, second=59)
    #                     last_open.write({'check_out': checkout_time})
    #                 # Create new attendance for this log as check_in
    #                 hr_attendance.create({
    #                     'employee_id': employee_id,
    #                     'check_in': log.punching_time,
    #                     'punch_date': punch_date
    #                 })
    #         else:
    #             # If minimal_attendance feature disabled, use alternate logic
    #             # (keeping your existing check_in_check_out logic)
    #             employee_list = []
    #             if employee_id in employee_list:
    #                 attd_id = self.check_in_check_out(employee_id, log.punching_time)
    #                 attendance = hr_attendance.browse(attd_id)
    #                 if attendance:
    #                     attendance.write({'check_out': log.punching_time})
    #                 employee_list.remove(employee_id)
    #             else:
    #                 attd_id = self.check_in_check_out(employee_id, log.punching_time)
    #                 attendance = hr_attendance.browse(attd_id)
    #                 if attendance and not attendance.check_out:
    #                     attendance.write({'check_out': log.punching_time})
    #                 else:
    #                     hr_attendance.create({
    #                         'employee_id': employee_id,
    #                         'check_in': log.punching_time
    #                     })
    #                     employee_list.append(employee_id)
    #
    #         # Now **automatic checkout logic for missing check-out in same day**
    #         # Only apply if minimal_attendance = True and we created a new attendance
    #         if minimal_attendance:
    #             # After above logic, check if the attendance for this employee/date has a check_out
    #             att_for_day = hr_attendance.search([
    #                 ('employee_id', '=', employee_id),
    #                 ('punch_date', '=', punch_date)
    #             ], limit=1)
    #             if att_for_day and not att_for_day.check_out:
    #                 # No checkout yet, so set it at 23:59:59 of the same day
    #                 checkout_time_local = att_for_day.check_in.replace(
    #                     hour=23, minute=59, second=59)
    #                 # Write this checkout if not already set
    #                 att_for_day.write({'check_out': checkout_time_local})
    #
    #         # Mark log processed
    #         log.is_calculated = True

    def calculate_attendance(self):
        tz = pytz.timezone('Asia/Karachi')  # Adjust to your timezone
        minimal_attendance = self.env['ir.config_parameter'].sudo().get_param(
            'tis_hr_biometric_attendance.minimal_attendance'
        )
        hr_attendance = self.env['hr.attendance']
        now = datetime.now(pytz.utc)
        today_str = now.strftime("%Y-%m-%d %H:%M:%S")

        domain = [
            ('punching_time', '<=', today_str),
            ('is_calculated', '=', False)
        ]
        attendance_logs = self.env['attendance.log'].search(domain)

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
