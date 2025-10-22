# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from datetime import datetime

from odoo import models


class AttendanceWizard(models.TransientModel):
    _name = 'attendance.calc.wizard'
    _description = 'attendance calc wizard'

    def calculate_attendance(self):
        minimal_attendance = self.env['ir.config_parameter'].sudo().get_param(
            'tis_hr_biometric_attendance.minimal_attendance')
        hr_attendance = self.env['hr.attendance']
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        domain = [('punching_time', '<=', str(today)), ('is_calculated', '=', False)]
        attendance_log = self.env['attendance.log'].search(domain)
        employee_list = []
        for log in attendance_log:
            if minimal_attendance:
                attendance = self.env['hr.attendance'].search(
                    [('employee_id', '=', log.employee_id.id),
                     ('punch_date', '=', log.punching_time.date())])
                if attendance:
                    attendance.write({'check_out': log.punching_time})
                else:
                    last_attendance_before_check_out = self.env['hr.attendance'].search([
                        ('employee_id', '=', log.employee_id.id),
                        ('check_out', '=', False)
                    ], order='check_in desc', limit=1)
                    if last_attendance_before_check_out:
                        check_out_time = last_attendance_before_check_out.check_in.replace(hour=23, minute=59,
                                                                                           second=59)
                        last_attendance_before_check_out.write({'check_out': check_out_time})
                    hr_attendance.create({'employee_id': log.employee_id.id, 'check_in': log.punching_time,
                                          'punch_date': log.punching_time.date()})
            else:
                if log.employee_id.id in employee_list:
                    attd = self.check_in_check_out(log.employee_id.id, log.punching_time)
                    attendance = self.env['hr.attendance'].search([('id', '=', attd)])
                    attendance.write({'check_out': log.punching_time})
                    employee_list.remove(log.employee_id.id)
                else:
                    attd = self.check_in_check_out(log.employee_id.id, log.punching_time)
                    attendance = self.env['hr.attendance'].search([('id', '=', attd)])
                    if attendance and attendance.check_out is False:
                        attendance.write({'check_out': log.punching_time})
                    else:
                        hr_attendance.create({'employee_id': log.employee_id.id, 'check_in': log.punching_time})
                        employee_list.append(log.employee_id.id)
            log.is_calculated = True

    def check_in_check_out(self, emp_id, time):
        attendances = self.env['hr.attendance'].search([('employee_id', '=', emp_id), ('check_out', '=', False)])
        if attendances:
            return attendances.id
