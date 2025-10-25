from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re

class InheritHrEmployee(models.Model):
    _inherit = 'hr.employee'

    bank_name = fields.Char(string="Bank Name", tracking=True)
    cheque_no = fields.Char(string="Cheque No", tracking=True)
    cheque_attachment = fields.Binary(string="Cheque Attachment", tracking=True)
    cheque_submission_date = fields.Date(string='Cheque Submission Date', default=fields.Date.context_today, tracking=True)
    education_ids = fields.One2many('employee.education', 'employee_id', string='Education Details')

    reference_ids = fields.One2many(
        'employee.reference',
        'employee_id',
        string='References'
    )

    employment_history_ids = fields.One2many(
        'employee.employment.history',
        'employee_id',
        string='Employment History'
    )

    professional_training_ids = fields.One2many(
        'employee.professional.training.history',
        'employee_id',
        string='Professional Trainings'
    )

    # --- Medical History Fields ---
    disability_1 = fields.Char(string='Disability 1')
    disability_1_date = fields.Date(string='Date')

    disability_2 = fields.Char(string='Disability 2')
    disability_2_date = fields.Date(string='Date')

    illness_or_chronic_disease = fields.Text(string='Any Illness or Chronic Disease')
    diagnosed_since = fields.Char(string='Diagnosed Since')

    surgeries = fields.Text(string='Surgeries / Operations')
    surgeries_date = fields.Date(string='Surgery / Operation Date')

    father_diabetes = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Father Diabetes'
    )
    father_hypertension = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Father Hypertension'
    )

    mother_diabetes = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Mother Diabetes'
    )
    mother_hypertension = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Mother Hypertension'
    )

    any_other_medical_info = fields.Text(string='Any Other Disease')

    next_of_kin_name = fields.Char("Next Of Kin Name")
    joining_date = fields.Date(string='Date of Joining')
    father_name = fields.Char("Father's Name")
    husband_name = fields.Char("Husband's Name")
    blood_group = fields.Char("Blood Group")

    driving_license_no = fields.Char("Driving License No")
    license_place_of_issuance = fields.Char("License Place Of Issuance")
    license_validity_date = fields.Date(string='License Validity Date')

    other_information = fields.Text("Other Information")

    asset_line_ids = fields.One2many(
        'employee.asset.line',
        'employee_id',
        string="Asset Handovers"
    )

    @api.model
    def add_note_line(self):
        self.ensure_one()
        self.asset_line_ids = [(0, 0, {'line_type': 'note'})]

    @api.constrains('cheque_no')
    def _check_cheque_no(self):
        for rec in self:
            if rec.cheque_no:
                if not re.fullmatch(r'^\d{6,10}$', rec.cheque_no):
                    raise ValidationError("Cheque No must be 6 to 10 digits long and numeric only.")