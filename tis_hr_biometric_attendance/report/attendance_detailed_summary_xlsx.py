from odoo import models
from datetime import datetime
import pytz

local_tz = pytz.timezone('Asia/Karachi')


class AttendanceDetailedSummaryXlsx(models.AbstractModel):
    _name = 'report.tis_hr_biometric_attendance.attendance_detailed_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    # def generate_xlsx_report(self, workbook, data, attendances):
    #     sheet = workbook.add_worksheet("Attendance Detailed Summary")
    #
    #     # Title format for the main heading
    #     title_format = workbook.add_format({
    #         'bold': True,
    #         'font_size': 16,
    #         'align': 'center',
    #         'valign': 'vcenter'
    #     })
    #
    #     header_format = workbook.add_format({
    #         'bold': True,
    #         'bg_color': '#4472C4',
    #         'font_color': '#FFFFFF',
    #         'align': 'center',
    #         'valign': 'vcenter',
    #         'border': 1,
    #         'text_wrap': True
    #     })
    #     date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1, 'align': 'center'})
    #     time_format = workbook.add_format({'num_format': 'hh:mm:ss', 'border': 1, 'align': 'center'})
    #     text_format = workbook.add_format({'border': 1, 'align': 'left'})
    #     center_format = workbook.add_format({'border': 1, 'align': 'center'})
    #
    #     def convert_to_local(dt, local_tz='Asia/Karachi'):
    #         if not dt:
    #             return dt
    #         utc = pytz.utc
    #         local = pytz.timezone(local_tz)
    #         if dt.tzinfo is None:
    #             dt_utc = utc.localize(dt)
    #         else:
    #             dt_utc = dt.astimezone(utc)
    #         dt_local = dt_utc.astimezone(local)
    #         return dt_local.replace(tzinfo=None)
    #
    #     # Write the main title in the first row, merged across all columns (0 to 7)
    #     sheet.merge_range(0, 0, 0, 7, "Attendance Detailed Summary", title_format)
    #     sheet.set_row(0, 30)  # Increase row height for title visibility
    #
    #     # Write headers in the second row (index 1)
    #     headers = ['Date', 'Employee', 'Check In', 'Check Out', 'Is Late', 'Late Minutes', 'Department', 'Company', 'Generated On']
    #     sheet.write_row(1, 0, headers, header_format)
    #
    #     # Freeze panes below header row (row 2)
    #     sheet.freeze_panes(2, 0)
    #
    #     row = 2  # Data starts from third row (index 2)
    #
    #     for att in attendances:
    #         employee = att.employee_id
    #         dept = employee.department_id.name if employee.department_id else ''
    #         company = employee.company_id.name if employee.company_id else ''
    #
    #         check_in = convert_to_local(att.check_in)
    #         check_out = convert_to_local(att.check_out)
    #         generated_on = convert_to_local(datetime.now(pytz.utc))
    #
    #         if check_in:
    #             sheet.write_datetime(row, 0, check_in.date(), date_format)
    #         else:
    #             sheet.write(row, 0, '', center_format)
    #
    #         sheet.write(row, 1, employee.name or '', text_format)
    #
    #         if check_in:
    #             sheet.write_datetime(row, 2, check_in, time_format)
    #         else:
    #             sheet.write(row, 2, '', center_format)
    #
    #         if check_out:
    #             sheet.write_datetime(row, 3, check_out, time_format)
    #         else:
    #             sheet.write(row, 3, '', center_format)
    #
    #         sheet.write(row, 4, 'Yes' if att.is_late else 'No', center_format)
    #         sheet.write(row, 5, dept, text_format)
    #         sheet.write(row, 6, dept, text_format)
    #         sheet.write(row, 6, company, text_format)
    #
    #         sheet.write_datetime(row, 8, generated_on, time_format)
    #
    #         row += 1
    #
    #     # Set column widths
    #     sheet.set_column(0, 0, 14)
    #     sheet.set_column(1, 1, 22)
    #     sheet.set_column(2, 3, 16)
    #     sheet.set_column(4, 4, 10)
    #     sheet.set_column(5, 6, 20)
    #     sheet.set_column(6, 6, 14)

    def generate_xlsx_report(self, workbook, data, attendances):
        sheet = workbook.add_worksheet("Attendance Detailed Summary")

        # Title format
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': '#FFFFFF',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'text_wrap': True,
        })

        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1, 'align': 'center'})
        time_format = workbook.add_format({'num_format': 'hh:mm:ss', 'border': 1, 'align': 'center'})
        text_format = workbook.add_format({'border': 1, 'align': 'left'})
        center_format = workbook.add_format({'border': 1, 'align': 'center'})

        # Convert timezone helper
        def convert_to_local(dt, local_tz='Asia/Karachi'):
            if not dt:
                return dt
            utc = pytz.utc
            local = pytz.timezone(local_tz)
            if dt.tzinfo is None:
                dt_utc = utc.localize(dt)
            else:
                dt_utc = dt.astimezone(utc)
            local_dt = dt_utc.astimezone(local)
            return local_dt.replace(tzinfo=None)

        # Main heading
        sheet.merge_range(0, 0, 0, 8, "Attendance Detailed Summary", title_format)
        sheet.set_row(0, 30)

        # Headers
        headers = [
            'Date', 'Employee', 'Check In', 'Check Out',
            'Is Late', 'Late Minutes', 'Department', 'Company', 'Generated On'
        ]
        sheet.write_row(1, 0, headers, header_format)

        sheet.freeze_panes(2, 0)  # Freeze header row

        row = 2

        for att in attendances:
            employee = att.employee_id

            # Fetch fields
            dept = employee.department_id.name if employee.department_id else ''
            company = employee.company_id.name if employee.company_id else ''

            check_in = convert_to_local(att.check_in)
            check_out = convert_to_local(att.check_out)
            generated_on = convert_to_local(datetime.now(pytz.utc))

            # Date
            if check_in:
                sheet.write_datetime(row, 0, check_in.date(), date_format)
            else:
                sheet.write(row, 0, '', center_format)

            # Employee name
            sheet.write(row, 1, employee.name or '', text_format)

            # Check-in/out times
            sheet.write_datetime(row, 2, check_in, time_format) if check_in else sheet.write(row, 2, '', center_format)
            sheet.write_datetime(row, 3, check_out, time_format) if check_out else sheet.write(row, 3, '',
                                                                                               center_format)

            # Is Late
            sheet.write(row, 4, 'Yes' if att.is_late else 'No', center_format)

            # Late Minutes (Fix)
            sheet.write(row, 5, att.late_minutes or 0, center_format)

            # Department
            sheet.write(row, 6, dept, text_format)

            # Company
            sheet.write(row, 7, company, text_format)

            # Generated On
            sheet.write_datetime(row, 8, generated_on, time_format)

            row += 1

        # Column widths
        sheet.set_column(0, 0, 14)
        sheet.set_column(1, 1, 22)
        sheet.set_column(2, 3, 16)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 7, 20)
        sheet.set_column(8, 8, 20)

