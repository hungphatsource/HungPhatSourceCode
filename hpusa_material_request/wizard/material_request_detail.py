
# -*- coding: utf-8 -*-
##############################################################################
##############################################################################

from osv import fields, osv
from tools.translate import _
from dateutil import relativedelta 
import time
from datetime import datetime
from datetime import timedelta
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw
import Image

class wizard_hpusa_material_request_report(osv.osv_memory):
    _name = "wizard.hpusa.material.request.report"
    _columns = {
            'date_from': fields.date('Date From', required=True),
            'date_to': fields.date('Date To', required=True),
            'so_id': fields.many2many('sale.order','material_request_sale_order_rel','request_sale_id','material_request_id', 'Sale Order'),
            'product_id': fields.many2one('product.product', 'Product'),
            'context':fields.html('Content')  ,
            'state':fields.selection([('get', 'get'),('choose','choose')]),
            'planning_id': fields.many2many('hpusa.manufacturing.planning','material_request_planning_rel','material_p_request_id','hpusa_planning_id','Planning'),
            'company_id': fields.many2one('res.company','Company'), 
     }
    _defaults={  
              'date_from': lambda *a: time.strftime('%Y-%m-01'),
              'date_to': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
              'state':'choose',
    }  
    
    def action_print(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])} 
        res = self.read(cr, uid, ids, ['date_from','date_to','so_id','product_id','planning_id','company_id'], context=context) 
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hpusa.material.request.report'   
        type = context.get('type_', '')
        if type == 'material_request_detail':
            datas['line'] = self.material_request_detail(cr, uid, res['date_from'], res['date_to'], res['so_id'] ,res['product_id'],res['company_id'])
            datas['line1'] = self.request_material_summary(cr, uid, res['date_from'], res['date_to'], res['so_id'] ,res['product_id'],res['planning_id'],res['company_id']) 
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'material_request_detail',
                'datas'         : datas,
           }
    # hpusa 08-07-2015    
        else:
            datas['line'] = self.request_material_summary(cr, uid, res['date_from'], res['date_to'], res['so_id'] ,res['product_id'],res['planning_id'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'material_request_summary',
                'datas'         : datas,
                }
      
    def view_material_request(self,cr,uid,ids,context=None):      
        datas = {'ids': context.get('active_ids', [])} 
        res = self.read(cr, uid, ids, ['date_from','date_to','so_id','product_id','planning_id','company_id'], context=context) 
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hpusa.material.request.report'   
        type = context.get('type_', '')
        if type == 'material_request_detail':
            datas['line'] = self.material_request_detail(cr, uid, res['date_from'], res['date_to'], res['so_id'] ,res['product_id'],res['company_id'])
            html = ""
            if datas['line']:
                html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BẢNG KÊ CHI TIẾT NGUYÊN VẬT LIỆU SẢN XUẤT </h1>'\
                '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                '<thead class = "theads">'\
                '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">Manufacturing Order</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">Manufacturing Date</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">Hp Style</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Product</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Material Code</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Material Name</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Qty</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Unit</th>'\
                '</tr>'\
                '</thead>'\
                '<tbody>'
                for i in datas['line']:
                    html += '<tr class = "trs">'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['production_name'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['mo_date'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['default_code'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['product'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['p_code'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['p_name'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['qty'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['unit'])+'</td>'\
                            '</tr>'
                html += '</tbody>'\
                        '</table>'\
                        '</span>'
            else :
                html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BẢNG KÊ CHI TIẾT NGUYÊN VẬT LIỆU SẢN XUẤT </h1>'\
                '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                '<thead class = "theads">'\
                '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">Default Code</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Product</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Material Code</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Material Name</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Unit</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Qty</th>'\
                '</tr>'\
                '</thead>'\
                '<tbody>'\
                '</tbody>'\
                '</table>'\
                '</span>'
            self.write(cr, uid,ids, {'state': 'get',
                                    'context':html }, context=context)   
        else:
            datas['line'] = self.request_material_summary(cr, uid, res['date_from'], res['date_to'], res['so_id'] ,res['product_id'],res['planning_id'],res['company_id'])
            html = ""
            if datas['line']:
                html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BẢNG KÊ TỔNG HỢP NGUYÊN VẬT LIỆU SẢN XUẤT </h1>'\
                '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                '<thead class = "theads">'\
                '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Material Code</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Material Name</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Unit</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Qty</th>'\
                '</tr>'\
                '</thead>'\
                '<tbody>'
                for i in datas['line']:
                    html += '<tr class = "trs">'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['p_code'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['p_name'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['unit'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['qty'])+'</td>'\
                            '</tr>'
                html += '</tbody>'\
                        '</table>'\
                        '</span>'
            else :
                html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BẢNG KÊ TỔNG HỢP NGUYÊN VẬT LIỆU SẢN XUẤT </h1>'\
                '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                '<thead class = "theads">'\
                '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >P Code</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >P Name</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Unit</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Qty</th>'\
                '</tr>'\
                '</thead>'\
                '<tbody>'\
                '</tbody>'\
                '</table>'\
                '</span>'
            self.write(cr, uid,ids, {'state': 'get',
                                    'context':html }, context=context)   
        return  {
             'type': 'ir.actions.act_window',
             'res_model': 'wizard.hpusa.material.request.report',
             'view_mode': 'form',
             'view_type': 'form',
             'res_id': res['id'],
             'views': [(False, 'form')],
             'target': 'new',
                }  
    
    def material_request_detail(self, cr, uid, date_from, date_to, so_id, product_id,company_id):
        arr =[]
        dt_to = datetime.strptime(date_to,'%Y-%m-%d')
        date_to= str(dt_to+relativedelta.relativedelta( days=1))[:10]
        
        sql = '''
                select mp.id as production_id
                ,mp.name as production_name 
                ,mp.mo_date 
                ,mp.bom_id
                ,pp.id as id
                ,pp.default_code as default_code
                ,pp.name_template as sp
                ,pu.name as dvt
                ,sum(mp.product_qty) as qty
                from mrp_production mp
                , sale_order so  
                , product_product pp  
                , product_uom pu
                , product_template pt  
            where to_date(to_char(mp.mo_date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
            and so.name = mp.origin
            and mp.product_id = pp.id
            and pt.uom_id = pu.id
            and pp.product_tmpl_id = pt.id
        '''%(date_from,date_to)
        if so_id:
            #sale_ids = str(so_id).replace('[', '(')
            #sale_ids = str(so_id).replace(']', ')')
            sql+='''
                and so.id = %s 
            '''%(so_id[0])
        if product_id:
           # product_ids = str(product_id).replace('[', '(')
            #product_ids = product_ids.replace(']', ')')
            sql+='''
                and mp.product_id = %s 
            '''%(product_id[0])
        if company_id:
            sql+='''
                and mp.company_id = %s 
            '''%(company_id[0]) 
               
        sql+='''
             
             group by mp.id,mp.name,pp.id,pp.default_code,pt.name,pu.name,mp.mo_date, mp.bom_id
             order by mp.name
             
        '''
        cr.execute(sql)
        print sql
        items = cr.dictfetchall()
        if items:
            for product in items:
                print product['id']
                
                arr.append({
                        'parent':'parent',
                        'production_name': product['production_name'],
                        'mo_date': product['mo_date'],
                        'default_code':product['default_code'],
                        'product': product['sp'],
                        'p_code':'',
                        'p_name':'',
                        'unit': product['dvt'],
                        'qty': product['qty'],
                        })
                lines= self.get_lines(cr,product['bom_id'])
                for line in lines:
                    arr.append({
                        'parent':'',
                        'production_name': '',
                        'mo_date': '',
                        'default_code':'',
                        'product':'',
                        'p_code':line['default_code'],
                        'p_name':line['p_name'],
    
                        'unit': line['unit'],
                        'qty': line['qty'], 
                            })
 
        return arr
    
    
    def get_lines(self,cr,bom_id):
       
        sql = '''
            select pp.default_code,pp.name_template as  p_name ,mrp.product_qty as qty ,pu.name as unit
            from mrp_bom mrp
            left join product_uom pu on mrp.product_uom = pu.id
            left join product_product pp on mrp.product_id=pp.id
            where bom_id = %s
            group by pp.default_code,pp.name_template  ,mrp.product_qty,pu.name
               order by pp.name_template
        '''%(bom_id)
       
        cr.execute(sql)
       # print sql 
        return cr.dictfetchall()
    
    def request_material_summary(self, cr, uid, date_from, date_to, so_id, product_id,planning_id,company_id):
       
        dt_to = datetime.strptime(date_to,'%Y-%m-%d')
        date_to= str(dt_to+relativedelta.relativedelta( days=1))[:10]
        arr=[]
        # -----------============== GET PRODUCTIONS IDS ====================------------------
        sql = '''
                select mp.id as id
                from mrp_production mp
                left join sale_order so on so.name = mp.origin
                left join product_template pt on mp.product_id = pt.id
                left join product_product pp on mp.product_id = pp.id
                left join product_uom pu on pt.uom_id = pu.id
            where to_date(to_char(mp.mo_date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
        '''%(date_from,date_to)
        if so_id:
            #sale_ids = str(so_id).replace('[', '(')
            #sale_ids = str(so_id).replace(']', ')')
            sql+='''
                and so.id = %s 
            '''%(so_id[0])
        if product_id:
            #product_ids = str(product_id).replace('[', '(')
            #product_ids = str(product_id).replace(']', ')')
            sql+='''
                and mp.product_id = %s 
            '''%(product_id[0])
        sql+='''
             group by mp.id,pp.default_code,pt.name,pu.name
             order by pt.name
        '''
        cr.execute(sql)
        items = cr.dictfetchall()
        
        production_ids = []
        for item in items:
            production_ids.append(item['id'])
        
        if planning_id:
            planning_ids =  str(planning_id).replace('[', '(')
            planning_ids = str(planning_ids).replace(']', ')')
            sql_production =''' 
            select mo_id as id
            from 
            hpusa_manufacturing_planning_line
            where planning_id in %s
            
            '''%(planning_ids)
            print sql_production
            cr.execute(sql)
            result = cr.dictfetchall()
            for item in result:
                
                production_ids.append(item['id'])
        print production_ids
        
        
    #---------------=============== GET MATERIAL SUMMARY ======================----------------
        sql_get_line = '''
             select pp.default_code as p_code
             ,pp.name_template as  p_name
             ,sum(mpbl.product_qty) as qty
             ,pu.name as unit
            from mrp_production_bom_line mpbl
            left join product_uom pu on mpbl.product_uom = pu.id
            left join product_product pp on mpbl.product_id=pp.id   
        '''
        if production_ids:
            production_id = str(production_ids).replace('[', '(')
            production_id = str(production_id).replace(']', ')')
            sql_get_line+= ' where mpbl.production_id in' +production_id
        sql_get_line+='''
               group by pp.default_code,pu.name,pp.name_template
               order by pp.name_template'''
        
        print sql_get_line
        cr.execute(sql_get_line)
        results = cr.dictfetchall()
        for result in results:
            
            arr.append({
                            'p_code':result['p_code'],
                            'p_name': result['p_name'],
                            'unit':  result['unit'],
                            'qty': result['qty'],
                            })
        return arr


openoffice_report.openoffice_report(
    'report.material_request_detail',
    'wizard.hpusa.material.request.report',
    parser=wizard_hpusa_material_request_report
) 

openoffice_report.openoffice_report(
    'report.material_request_summary',
    'wizard.hpusa.material.request.report',
    parser=wizard_hpusa_material_request_report
) 



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
