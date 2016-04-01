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
from openerp.osv import fields, osv

# Available commission rule
COMMISSION_RULE = [('percent_fixed', 'Fixed Commission Rate'),
                      ('percent_product_category', 'Product Category Commission Rate'),
                      ('percent_product', 'Product Commission Rate'),
                      ('percent_product_step', 'Product Commission Rate Steps'),
                      ('percent_amount', 'Commission Rate By Order Quantity')]


class commission_rule(osv.osv):

    _name = "commission.rule"
    _description = "Commission Rule"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'type': fields.selection(COMMISSION_RULE, 'Type', required=True),
        'secondary': fields.many2one('commission.rule','Second Rule'),
        'fix_percent': fields.float('Fix Percentage'),
        'rule_rates': fields.one2many('commission.rule.rate', 'commission_rule_id', 'Rates'),
        'rule_conditions': fields.one2many('commission.rule.condition', 'commission_rule_id', 'Conditions'),
        'active': fields.boolean('Active'),
        'sale_team_ids': fields.one2many('sale.team', 'commission_rule_id', 'Teams'),
        'salesperson_ids': fields.one2many('res.users', 'commission_rule_id', 'Salesperson'),
    }
    _defaults = {
        'active': True
    }

commission_rule()

  
class commission_rule_rate(osv.osv):

    _name = "commission.rule.rate"
    _description = "Commission Rule Rate"
    _columns = {
        'commission_rule_id': fields.many2one('commission.rule', 'Commission Rule'),
        'quantity_over': fields.float('Quantity Over', required=True),
        'quantity_upto': fields.float('Quantity Up-To', required=True),
        'percent_commission': fields.one2many('commission.rule.rate.line','commission_line_master','Rule Commission Amount', required=True),
        
    }
    _order = 'id'

commission_rule_rate()

class commission_rule_rate_line(osv.osv):
    _name = "commission.rule.rate.line"
    _description = "Commission Rule Rate line"
    _columns = {        
        'commission_line_master': fields.many2one('commission.rule.rate','Lines'),      
        'amount_over': fields.float('Amount Over', required=True),
        'amount_upto': fields.float('Amount Up-To', required=True),
        'amount_commission': fields.float('Commission Amount for Diamon', required=True),
    }
    _order = 'id'
commission_rule_rate_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
