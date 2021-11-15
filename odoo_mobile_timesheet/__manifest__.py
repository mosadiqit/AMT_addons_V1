# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mobile Timesheet Odoo',
    'version': '1.2',
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
    'live_test_url': '',
    'depends': [
        'website',
        'hr_timesheet',
        'analytic',
        'portal',
        'project',
    ],
    'data': [
        'data/work_type_data.xml',
        'security/ir.model.access.csv',
        'views/website_portal_templates.xml',
        'views/project_view.xml',
        'views/task_view.xml',
        'views/timesheet_work_type_view.xml',
        'views/timesheet_line_view.xml',
     ],
    'category': 'Human Resources',
    'summary':  """This app allow your Internal user to fill Timesheet in Mobile and Tablets. All types of mobile are supported (Android and IOS).""",
    'description': """
odoo mobile timesheet,
mobile timesheet,
Mobile Timesheet User,
Timesheet Internal User,
Odoo Mobile Timesheet User,

     """,
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
