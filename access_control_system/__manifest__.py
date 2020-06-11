# -*- coding: utf-8 -*-

{
    'name': 'Access Control',
    'description': 'Manage access control of devices.',
    'author': 'TDL',
    'depends': ['base','hr','contacts'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/acs_menu.xml',
        'views/acs_view.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
}

