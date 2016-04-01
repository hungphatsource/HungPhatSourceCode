# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2004-2012 OpenERP S.A. <http://openerp.com>
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

import base64
import cStringIO
import xlwt
from openerp import tools
from openerp.osv import fields,osv
from openerp.tools.translate import _
from openerp.tools.misc import get_iso_codes
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw
from dateutil import relativedelta 
import time
from datetime import date
from datetime import datetime

class agent_detail_report(osv.osv_memory):
    _name = "agent_detail_report"

    _columns = {
            'start_date': fields.date(u'Start Date',required=True),
            'end_date': fields.date(u'End Date', required=True),
            'agent_type': fields.selection([('All', 'All'), ('Agent', 'Agent'),('cooperate', 'Cooperate')], 'Type',),
            'type_report': fields.selection([('summary', 'Commission Summary'), ('liabilities', 'Liabilities'),('detail', 'Commission Detail') ],'Report Type', required=True),
            'agent_cooperate': fields.many2one('res.users','Agent-Cooperate'),
            'name': fields.char('File Name', readonly=True),

            'data': fields.binary('File', readonly=True),
            'state': fields.selection([('choose', 'choose'),   # choose language
                                       ('get', 'get')])        # get the file
    }
    _defaults = {
        'state': 'choose',
        'name': 'agent_report.xls',
        'start_date': lambda *a: time.strftime('%Y-%m-01'),
        'end_date': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }

    def act_getfile(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        datas = {'ids': context.get('active_ids', [])} 
        res = self.read(cr, uid, ids, ['start_date','end_date',], context=context) 
        res = res and res[0] or {}
        datas['form'] = res
        datas['model'] = 'sale.order'   
        if this.type_report == 'summary':
            datas['line'] = self.summary(cr, uid, this)
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'commission_summary',
                'datas'         : datas,
           } 
        if this.type_report == 'liabilities':
            datas['line'] = self.liabilities_agent(cr, uid, this)
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'liabilities',
                'datas'         : datas,
           }    
        if this.type_report == 'detail':
            datas['line'] = self.detail(cr, uid, this)
            datas['form']['code'] = this.agent_cooperate.partner_id.name
            datas['form']['name'] = this.agent_cooperate.code
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'commission_detail',
                'datas'         : datas,
           }    
    def summary(self, cr, uid, obj):
        res = []
        total_amount = 0
        total_payment = 0
        total_remain = 0
        total_commission = 0
        total_level = 0
        total_qty = 0
        query = ''
        if obj.agent_type == 'Agent':
            query += ''' AND us.option_choose = 'agent' '''
        if obj.agent_type == 'cooperate':
            query += ''' AND us.option_choose = 'cooperate' '''
        if obj.agent_cooperate:
            query += ''' AND us.id = %s '''%(obj.agent_cooperate.id)
        sql = '''
                SELECT pa.name, us.option_choose, SUM(inv.amount_total) as total, 
                        SUM(inv.amount_total - inv.residual) as payment, 
                        SUM(inv.residual) as remain, SUM(inv_l.quantity) as qty, MAX(line.sku) as sku, coalesce(SUM(line.commission_amt + line.adjust_amt),0) as commission
                FROM res_users us
                LEFT JOIN res_partner pa ON(pa.id = us.partner_id)
                LEFT JOIN sale_order sa ON(sa.user_id = us.id)
                LEFT JOIN sale_order_invoice_rel rel ON(rel.order_id =  sa.id)
                LEFT JOIN account_invoice inv ON(inv.id = rel.invoice_id)
                LEFT JOIN account_invoice_line inv_l ON( inv_l.invoice_id = inv.id)
                LEFT JOIN commission_worksheet_line line ON(line.invoice_id = inv.id AND line.product_name = inv_l.product_id)
                LEFT JOIN commission_worksheet cw ON(cw.id = line.worksheet_id)
                WHERE us.option_choose IS NOT NULL AND sa.date_order >= '%s' AND sa.date_order <= '%s'  %s
                GROUP BY pa.name, us.option_choose
                 ''' %(obj.start_date, obj.end_date, query)
        cr.execute(sql)
        print sql
        result = cr.dictfetchall()  
        for i in result:
            str_option = '' 
            if i['option_choose'] == 'agent':
                str_option = 'Đại Lý'
            else:
                str_option = 'Cộng Tác Viên'
            total_amount += i['total']
            total_payment += i['payment']
            total_remain += i['remain']
            total_commission += i['commission']
            if i['sku']:
                total_level += i['sku'] or 0
            total_qty += i['qty']
            res.append({
                        'name': i['name'],
                        'option' : str_option,
                        'qty' : i['qty'],
                        'amount' : i['total'],
                        'payment' : i['payment'],
                        'remain':  i['remain'],
                        'commission': i['commission'],
                        'level': i['sku'],
                        })       
        
        return {'line':res, 'total_amount': total_amount, 'total_payment': total_payment, 'total_remain': total_remain, 'total_commission': total_commission, 'total_level': total_level, 'total_qty': total_qty}

    def detail(self, cr, uid, obj):
        res = []
        query = ''
        if obj.agent_type == 'Agent':
            query += ''' AND us.option_choose = 'agent' '''
        if obj.agent_type == 'cooperate':
            query += ''' AND us.option_choose = 'cooperate' '''
        if obj.agent_cooperate:
            query += ''' AND us.id = %s '''%(obj.agent_cooperate.id)
        sql = ''' 
             SELECT sa.name as so_name, sa.date_order as so_date, pp.default_code as p_code, pp.name_template as p_name, inv_l.quantity as qty,  inv.amount_total - inv.residual as payment, inv.residual as debit, inv.date_due, line.invoice_amt as unit, line.discount as discount, line.amount as total, line.commission_amt, line.adjust_amt
                FROM res_users us
                LEFT JOIN res_partner pa ON(pa.id = us.partner_id)
                LEFT JOIN sale_order sa ON(sa.user_id = us.id)
                LEFT JOIN sale_order_invoice_rel rel ON(rel.order_id =  sa.id)
                LEFT JOIN account_invoice inv ON(inv.id = rel.invoice_id)
                LEFT JOIN account_invoice_line inv_l ON( inv_l.invoice_id = inv.id)
                LEFT JOIN product_product pp ON(pp.id = inv_l.product_id)
                LEFT JOIN commission_worksheet_line line ON(line.invoice_id = inv.id AND line.product_name = inv_l.product_id)
                LEFT JOIN commission_worksheet cw ON(cw.id = line.worksheet_id)
                WHERE line.id IS NOT NULL AND us.option_choose IS NOT NULL AND sa.date_order >= '%s' AND sa.date_order <= '%s' AND us.id = %s %s               
                 '''%(obj.start_date, obj.end_date, obj.agent_cooperate.id, query)
        cr.execute(sql)
        print sql
        result = cr.dictfetchall()  
        qty = 0
        unit = 0
        discount = 0
        total = 0
        payment = 0
        debit = 0
        total_commission_amt = 0
        total_adjust_amt= 0
        for i in result:
            commission_amt = i['commission_amt'] or 0
            adjust_amt = i['adjust_amt'] or 0
            qty += i['qty']
            unit += i['unit']
            discount += i['discount']
            total += i['total']
            payment += i['payment']
            debit += i['total'] - i['payment']
            total_commission_amt += commission_amt
            total_adjust_amt += adjust_amt
            res.append({
                        'so_name': i['so_name'],
                        'so_date': i['so_date'],
                        'p_code': i['p_code'],
                        'p_name': i['p_name'],
                        'qty': i['qty'],
                        'unit': i['unit'],
                        'discount': i['discount'],
                        'total': i['total'],
                        'payment': i['payment'],
                        'debit': i['debit'],
                        'date_due': i['date_due'],
                        'commission_amt': commission_amt or 0,
                        'adjust_amt': adjust_amt or 0,
                        })
        return {'line': res, 'qty': qty, 'unit': unit, 'discount': discount, 'total': total, 'payment': payment, 'debit': debit, 'total_commission_amt': total_commission_amt, 'total_adjust_amt': total_adjust_amt} 


    def liabilities_agent(self, cr, uid, obj):
        res = []
        res_1 = []
        query = ''
        total_pay1 = 0
        total_pay2 = 0
        pay_1 = 0
        pay_2 = 0
        debit1 = 0
        debit2 = 0
        
        if obj.agent_type == 'Agent':
            query += ''' AND us.option_choose = 'agent' '''
        if obj.agent_type == 'cooperate':
            query += ''' AND us.option_choose = 'cooperate' '''
        if obj.agent_cooperate:
            query += ''' AND us.id = %s '''%(obj.agent_cooperate.id)
        sql = '''SELECT DISTINCT pa.name as name, us.option_choose, coalesce(SUM(inv.amount_total),0) as amount, coalesce(SUM(inv.amount_total - inv.residual),0) as payment, MAX(pa.credit_limit) as credit_limit
                FROM res_partner pa
                LEFT JOIN res_users us ON(us.partner_id = pa.id)
                LEFT JOIN sale_order sa ON(sa.user_id = us.id)
                LEFT JOIN sale_order_invoice_rel rel ON(rel.order_id =  sa.id)
                LEFT JOIN account_invoice inv ON(inv.id = rel.invoice_id)
                WHERE us.option_choose IS NOT NULL AND inv.state <> 'draft' AND sa.date_order >= '%s' AND sa.date_order <= '%s' %s
                GROUP BY pa.name, us.option_choose
          HAVING coalesce(SUM(inv.residual),0) > 0''' %(obj.start_date, obj.end_date, query)
        cr.execute(sql)
        print sql
        result = cr.dictfetchall()  
        for i in result:  
            str_limit = ''
            if i['credit_limit']:
                if i['amount'] - i['payment'] > i['credit_limit']:
                    str_limit = 'Tăng'
                elif i['amount'] - i['payment'] == i['credit_limit']:
                    str_limit = 'Bằng'
                else:
                    str_limit = 'Giảm'
            remain =  i['amount'] and float(i['amount']) or 0 - i['payment'] and float(i['payment']) or 0
            if i['option_choose'] == 'agent':
                stt = len(res) + 1
                total_pay1 += i['amount']
                pay_1 += i['payment']
                debit1 += remain
                res.append({
                        'stt': stt,
                        'name': i['name'],
                        'amount' : i['amount'],
                        'payment' : i['payment'],
                        'remain': remain ,
                        'limit': i['credit_limit'],
                        'str_limit': str_limit,
                        }) 
            else:
                stt = len(res_1) + 1
                total_pay2 += i['amount']
                pay_2 += i['payment']
                debit2 += remain
                res_1.append({
                        'stt': stt,
                        'name': i['name'],
                        'amount' : i['amount'],
                        'payment' : i['payment'],
                        'remain':  remain ,
                        'limit': i['credit_limit'],
                        'str_limit': str_limit,
                        }) 
                
        return {'line1':res, 'line2': res_1, 'total_pay1': total_pay1, 'pay_1': pay_1, 'debit1': debit1, 'total_pay2': total_pay2, 'pay_2': pay_2, 'debit2': debit2}

        
       
openoffice_report.openoffice_report(
    'report.commission_summary',
    'sale.order',
    parser=agent_detail_report
) 

openoffice_report.openoffice_report(
    'report.liabilities',
    'sale.order',
    parser=agent_detail_report
) 

openoffice_report.openoffice_report(
    'report.commission_detail',
    'sale.order',
    parser=agent_detail_report
) 
