# -*- coding: utf-8 -*-
# This module and its content is copyright of Exceed Logics Pvt. Ltd .
# - © Exceed Logics Pvt. Ltd 2025. All rights reserved.

{
    'name': 'AAW Employee Customization',
    'version': '18.0.0.0',
    'category': 'Human Resources',
    'sequence': 1,
    'author': 'Haseeb Ahmad',
    'summary': 'Biometric attendance integration',
    'website': 'exceedlogics.com/',
    'currency': 'PKR',
    'license': 'Other proprietary',
    'description': """
        Customization of Employee Form""",
    'depends': ['base','hr'],
    'data': [
        "security/hr_security.xml",
        "security/ir.model.access.csv",
        "views/inherit_hr_employee.xml",
        "views/employee_education_degree_views.xml",
        "views/menus.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
