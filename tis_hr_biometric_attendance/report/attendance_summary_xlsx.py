from odoo import models

class AttendanceSummaryXlsx(models.AbstractModel):
    _name = 'report.tis_hr_biometric_attendance.attendance_summary_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, summaries):
        # Create sheet
        sheet = workbook.add_worksheet('Attendance Summary')

        # Formats
        title_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'
        })
        bold_center = workbook.add_format({
            'bold': True, 'bg_color': '#D3D3D3', 'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd', 'align': 'center', 'border': 1
        })
        center = workbook.add_format({
            'align': 'center', 'border': 1
        })
        wrap_text = workbook.add_format({
            'text_wrap': True, 'border': 1
        })

        # Merge top row for main title
        sheet.merge_range('A1:J1', 'Attendance Summary Report', title_format)
        row = 2  # Start from row 3 for headers

        # Header row
        headers = [
            'Employee',
            'Department',
            'Start Date',
            'End Date',
            'Total Working Days',
            'Present Days',
            'Leave Days',
            'Absent Days',
            'Late Count',
            'Generated On',
        ]

        for col, header in enumerate(headers):
            sheet.write(row, col, header, bold_center)

        # Data rows
        row += 1
        for summary in summaries.exists():  # skip deleted records
            sheet.write(row, 0, summary.employee_id.name or '', center)
            sheet.write(row, 1, summary.department_id.name or '', center)
            sheet.write_datetime(row, 2, summary.date_from, date_format)
            sheet.write_datetime(row, 3, summary.date_to, date_format)
            sheet.write(row, 4, summary.total_days or 0, center)
            sheet.write(row, 5, summary.present_days or 0, center)
            sheet.write(row, 6, summary.leave_days or 0, center)
            sheet.write(row, 7, summary.absent_days or 0, center)
            sheet.write(row, 8, summary.late_count or 0, center)
            sheet.write_datetime(row, 9, summary.summary_date, date_format)
            row += 1

        # Auto-adjust column width
        sheet.set_column(0, 1, 20)  # Employee, Department
        sheet.set_column(2, 3, 14)  # Dates
        sheet.set_column(4, 9, 18)  # Numbers

        # Optional: Freeze header row
        sheet.freeze_panes(3, 0)  # Freeze first 3 rows (title + header)
