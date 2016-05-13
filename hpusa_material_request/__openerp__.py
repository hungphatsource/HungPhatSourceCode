# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Hpusa Material Request',
    'version': '1.0',
    'category': 'HPUSA',
    'sequence': 14,
    'author': 'lieuthanhthuan@gmail.com',
    'website' : '',
    'depends': ['mrp','sale','base','hpusa_manufacturing','hpusa_manufacturing_planning','hpusa_manufacturing2'],
    'data': [
            'view/mrp_view.xml',
            'report/wizard_hpusa_material_request_report.xml',
            'wizard/material_request_report_view.xml',
            'view/hpusa_metal.xml',
            #'wizard/list_mo_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
