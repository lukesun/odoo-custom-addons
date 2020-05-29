# -*- coding: utf-8 -*-

{
    'name': 'Access Control',
    'description': 'Manage access control devices.',
    'author': 'TDL',
    'depends': ['base'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/acs_menu.xml',
        'views/acs_view.xml',
        'views/templates.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
}

