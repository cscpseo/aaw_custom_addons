# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, time


class AttendanceLog(models.Model):
    _name = 'attendance.log'
    _description = 'attendance log'
    _order = 'punching_time'
    _rec_name = 'punching_time'

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    status = fields.Selection([('0', 'Check In'),
                               ('1', 'Check Out'),
                               ('2', 'Punched')], string='Status', readonly=True)
    punching_time = fields.Datetime('Punching Time', readonly=True)
    is_calculated = fields.Boolean('Calculated', default=False, readonly=True)
    device = fields.Char('Device', readonly=True)
    # company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="employee_id.company_id")


    def unlink(self):
        if any(self.filtered(lambda log: log.is_calculated == True)):
            raise UserError(('You cannot delete a Record which is already Calculated !!!'))
        return super(AttendanceLog, self).unlink()


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    punch_date = fields.Date(string='Punch Date')

    scheduled_checkin_time = fields.Datetime(
        string="Scheduled Check-In Time",
        default=lambda self: datetime.combine(fields.Datetime.now().date(), time(9, 0, 0))
    )
    is_late = fields.Boolean(
        string="Is Late?",
        compute="_compute_late",
        store=True
    )
    late_minutes = fields.Integer(
        string="Late Minutes",
        compute="_compute_late",
        store=True
    )

    @api.depends('check_in')
    def _compute_late(self):
        user_tz_str = self.env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz_str)
        for rec in self:
            if rec.check_in:
                # Convert UTC stored check_in to user's local timezone
                local_dt = fields.Datetime.context_timestamp(rec, rec.check_in)
                # Now build threshold at 09:15 of that local date
                threshold = local_dt.replace(hour=9, minute=16, second=0, microsecond=0)
                if local_dt > threshold:
                    diff = local_dt - threshold
                    rec.late_minutes = int(diff.total_seconds() / 60)
                    rec.is_late = True
                else:
                    rec.late_minutes = 0
                    rec.is_late = False
            else:
                rec.late_minutes = 0
                rec.is_late = False


    def compute_in_out_difference(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                check_in = datetime.strptime(str(attendance.check_in), '%Y-%m-%d %H:%M:%S')
                check_out = datetime.strptime(str(attendance.check_out), '%Y-%m-%d %H:%M:%S')
                diff1 = check_out - check_in
                total_seconds = diff1.seconds
                diff2 = total_seconds / 3600.0
                attendance.in_out_diff = diff2
            else:
                attendance.in_out_diff = 0

    in_out_diff = fields.Float('Difference', compute='compute_in_out_difference')

    def unlink(self):
        for record in self:
            domain = [('employee_id', '=', record.employee_id.id), '|',
                      ('punching_time', '=', record.check_in),
                      ('punching_time', '=', record.check_out)]
            attend_obj = self.env['attendance.log'].search(domain)
            for log in attend_obj:
                log.is_calculated = False
        return super(HrAttendance, self).unlink()
