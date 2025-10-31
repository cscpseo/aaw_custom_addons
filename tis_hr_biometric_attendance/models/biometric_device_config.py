# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from collections import defaultdict
from odoo.addons.base.models.res_partner import _tz_get
import pytz
from datetime import datetime
from ..zk import ZK
from odoo.exceptions import UserError, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)

class BiometricDeviceConfig(models.Model):
    _name = 'biometric.config'
    _description = 'Biometric Configuration'

    name = fields.Char(string='Name', required=True)
    device_ip = fields.Char(string='Device IP', required=True)
    port = fields.Integer(string='Port', required=True)
    is_password_set = fields.Boolean(string='Is Password Set', default=False)
    device_password = fields.Char(string='Device Password')
    time_zone = fields.Selection(_tz_get, string='Timezone', default=lambda self: self.env.user.tz or 'GMT')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, readonly=True)

    @api.constrains('device_ip')
    def _check_device_ip(self):
        """Validation if Same Device IP Already Exists"""
        for config in self:
            existing_configuration = self.env['biometric.config'].search([('device_ip','=',config.device_ip)])
            if existing_configuration:
                raise ValidationError('Device IP already configured')

    @api.onchange('is_password_set')
    def on_is_password_set_change(self):
        if not self.is_password_set:
            self.device_password = ''

    @api.onchange('device_password')
    def _check_password(self):
        if self.device_password and not self.device_password.isdigit():
            raise UserError(_("Device password should only contain numeric characters."))

    def test_device_connection(self):
        ip = self.device_ip
        port = self.port
        password = self.device_password
        _logger.info("Testing device connection: IP=%s, Port=%s", ip, port)
        zk = ZK(ip, port, password=password)
        _logger.info("ZK Instance Created: %s", zk)
        try:
            conn = zk.connect()
            if conn:
                raise UserError(_("Connection Success"))
            else:
                raise ValidationError(_("Connection Failed"))
        except Exception as e:
            raise UserError(str(e))

    def sync_employees(self):
        uid = 0
        employees = self.env['hr.employee'].search([])
        next_user_id = 1
        uid_list = []
        user_id_list = []
        ip = self.device_ip
        port = self.port
        password = self.device_password
        zk = ZK(ip, port, password=password)
        try:
            conn = zk.connect()
            if conn:
                users = zk.get_users()

                def create_next_user_id(user_id):
                    pattern = r'(\d+)'
                    def increment(match):
                        number = match.group(0)
                        incremented_number = str(int(number) + 1)
                        return incremented_number
                    return re.sub(pattern, increment, user_id)

                if users:
                    for user in users:
                        uid_list.append(user.uid)
                        user_id_list.append(user.user_id)
                    uid_list.sort()
                    user_id_list.sort()
                    uid = uid_list[-1]
                    user_id = str(user_id_list[-1])
                    next_user_id = create_next_user_id(user_id)
                    num = 2
                    while True:
                        if next_user_id in user_id_list:
                            user_id = str(user_id_list[-1 * num])
                            next_user_id = create_next_user_id(user_id)
                            num += 1
                        else:
                            for _ in range(len(employees)):
                                test_user_id = create_next_user_id(next_user_id)
                                if test_user_id in user_id_list:
                                    next_user_id = test_user_id
                                    continue
                            break

                for employee in employees:
                    biometric_device = employee.biometric_device_ids.search(
                        [('employee_id', '=', employee.id), ('device_id', '=', self.id)])
                    if not biometric_device:
                        uid += 1
                        employee.biometric_device_ids = [(0, 0, {
                            'employee_id': employee.id,
                            'biometric_attendance_id': next_user_id,
                            'device_id': self.id,
                        })]
                        zk.set_user(uid, employee.name, 0, '', '', str(next_user_id), card=employee.pin)
                        next_user_id = create_next_user_id(next_user_id)

                return {
                    'name': 'Success Message',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee.sync.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new'
                }
            else:
                raise ValidationError("Connection Failed")
        except Exception as e:
            raise UserError(str(e))

    def download_attendance_log(self):
        attend_obj = self.env['attendance.log']
        ip = self.device_ip
        port = self.port
        password = self.device_password
        zk = ZK(ip, port, password=password)

        try:
            conn = zk.connect()
            if not conn:
                raise ValidationError("Connection failed")

            attendances = zk.get_attendance()
            if not attendances:
                raise UserError(_("No logs found on device."))

            device_name = self.name
            company_id = self.company_id

            attendence_list = []

            # Step 1: Prepare raw attendance list
            for attendance in attendances:
                atten_time = attendance.timestamp
                local_tz = pytz.timezone(self.time_zone or 'GMT')
                local_dt = local_tz.localize(atten_time, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                naive_utc_dt = utc_dt.replace(tzinfo=None)

                employees = self.env['biometric.attendance.devices'].search([
                    ('biometric_attendance_id', '=', attendance.user_id),
                    ('device_id', '=', self.id)
                ])

                if len(employees) > 1:
                    employee_names = employees.mapped('employee_id.name')
                    raise UserError(
                        _("Multiple employees linked with same Biometric ID: %s") % ', '.join(employee_names))

                if not employees:
                    continue  # skip if not found

                attendence_list.append({
                    'user_id': attendance.user_id,
                    'employee_id': employees.employee_id.id,
                    'atten_time': naive_utc_dt,
                })

            # Step 2: Sort and group by user + date
            sorted_attendance = sorted(attendence_list, key=lambda x: (x['user_id'], x['atten_time']))
            employee_daywise = defaultdict(list)

            for entry in sorted_attendance:
                date_key = (entry['user_id'], entry['atten_time'].date())
                employee_daywise[date_key].append(entry)

            # Step 3: Assign Check-in / Check-out per day
            for (user_id, punch_date), entries in employee_daywise.items():
                entries = sorted(entries, key=lambda x: x['atten_time'])
                for i, entry in enumerate(entries):
                    status = '0' if i % 2 == 0 else '1'  # even = check-in, odd = check-out
                    employee_id = entry['employee_id']
                    punching_time = entry['atten_time']

                    existing_log = attend_obj.search([
                        ('employee_id', '=', employee_id),
                        ('punching_time', '=', punching_time)
                    ], limit=1)

                    vals = {
                        'employee_id': employee_id,
                        'punching_time': punching_time,
                        'status': status,  # 0 = in, 1 = out
                        'device': str(device_name),
                        'company_id': company_id.id,
                        'is_calculated': existing_log.is_calculated if existing_log else False
                    }

                    if existing_log:
                        existing_log.write(vals)
                    else:
                        attend_obj.create(vals)

            return {
                'name': 'Success Message',
                'type': 'ir.actions.act_window',
                'res_model': 'success.wizard',
                'view_mode': 'form',
                'target': 'new'
            }

        except Exception as e:
            raise UserError(str(e))

    def download_attendance_log_new(self):
        devices = self.env["biometric.config"].search([])
        for device in devices:
            device.download_attendance_log()
