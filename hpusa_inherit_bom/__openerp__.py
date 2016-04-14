# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Nicolas Bessi (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
##############################################################################

{
    'name': 'inherit Bom',
    'description': '',
    'version': '0.9',
    'depends': ['base','web' ,'hpusa_manufacturing' , 'mrp' ,'hpusa_product_quality'],
    'author': 'HungPhatUSA',
    'category': 'Reporting', # i.e a technical module, not shown in Application install menu
    'url': '',
    'update_xml': [
          'inherit_view_bom.xml',
         
             ],
    'installable': True,
    'auto_install': False,
    'images': ['',],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: