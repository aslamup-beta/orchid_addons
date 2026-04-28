# -*- encoding: utf-8 -*-
{
    'name': 'Orchid Print Excel',
    'version': '1.0',
    'category': 'Web',
    'description': """
        This helps to export tree view in to excel report
    """,
    'author': 'OrchidERP',
    'website': 'http://www.orchiderp.com',
    'depends': ['web'],
    'data': ['views/printscreen.xml'],
    'qweb': ['static/src/xml/printscreen_export.xml'],
    'installable': True,
    'auto_install': False,
    'web_preload': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
