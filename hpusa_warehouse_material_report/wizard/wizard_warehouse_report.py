
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
import this
from decimal import Context

class wizard_hpusa_material_request_report(osv.osv):
    _name = "wizard.hpusa.warehouse.report"
    
    _columns = {
            'month_from':  fields.selection([('01','January'),
                                       ('02','Feburary'),
                                       ('03','March'),
                                       ('04','April'),
                                       ('05','May'),
                                       ('06','June'),
                                       ('07','July'),
                                       ('08','August'),
                                       ('09','Septemper'),
                                       ('10','October'),
                                       ('11','November'),
                                       ('12','Deccember'),
                                       ],'Month From'),
            'month_to':  fields.selection([('01','January'),
                                       ('02','Feburary'),
                                       ('03','March'),
                                       ('04','April'),
                                       ('05','May'),
                                       ('06','June'),
                                       ('07','July'),
                                       ('08','August'),
                                       ('09','Septemper'),
                                       ('10','October'),
                                       ('11','November'),
                                       ('12','Deccember'),
                                       ],'Month To'),
            'month': fields.selection([('01','January'),
                                       ('02','Feburary'),
                                       ('03','March'),
                                       ('04','April'),
                                       ('05','May'),
                                       ('06','June'),
                                       ('07','July'),
                                       ('08','August'),
                                       ('09','Septemper'),
                                       ('10','October'),
                                       ('11','November'),
                                       ('12','Deccember'),
                                       ],'Month'),
                
            'year_id': fields.many2one('year.configuration', 'Year', required=True),
            'stock_ids': fields.many2one('hpusa.report.configuration' ,'Location', required=True),
            'category_id': fields.many2one('product.category', 'Category', required=True),
            'context':fields.html('Content')  ,
            'state':fields.selection([('get', 'get'),('choose','choose')]),
            'option':fields.selection([('view', 'Report Month'),('export','Report Year')] , 'Option' , required=True),
            'type_report': fields.selection([('raw','Raw Materials'),('diamond','Diamonds'),('general','Inventory Report')],'Report Type', required=True)
     }
    
    _defaults={  
              'month_from': '01',
              'month_to': '12',
              'month':'01',
              'state':'choose',
              'year_id':1,
              'option': 'view',
              'type_report': 'raw', 
              'stock_ids':1,  
              'category_id':1,     
    }
    
    def onchange_report_type(self,cr,uid,ids,report_type,stock_config_id,context=None):
        #===================== Change Product Categories ===================================
        values={}
        if report_type and stock_config_id:
            conf = self.pool.get('hpusa.report.configuration').browse(cr,uid,stock_config_id)
            if conf:
                if report_type=='raw':
                    values['category_id'] = conf.raw_category.id
                elif report_type=='general':
                    values['option'] = 'view'
                else:
                    
                    values['category_id'] = conf.diamond_category.id
        return {'value':values}
    
    def action_export(self, cr, uid, ids, context=None):
        
        #======================= Export Data to EXCEL ============================================
        this = self.browse(cr, uid,ids,context =None)[0]
        datas = {'ids': context.get('active_ids', [])} 
        res = self.read(cr, uid, ids, ['month_from','month_to','month','year_id','stock_ids','option','type_report','category_id'], context=context) 
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hpusa.warehouse.report' 
        
        for i in range(1,13):
            key = 'line'+str(i)
            datas[key]=[]
        
        
        if res['type_report']=='raw':
            #====================== REPORT RAW MATERIAL ===========================
            if res['option']=='view':
                #===================== lấy dữ liệu báo cáo vàng của 1 tháng ================================
                if  res['month']!=False:
                    month_to = str(this.year_id.name)  +'-'+ res['month']+ '-01'
                    mt_to = datetime.strptime(month_to,'%Y-%m-%d')
                    next_month= str(mt_to+relativedelta.relativedelta( months=1))[:10]
                   
                    datas['line1']  = self.export_rawmaterial_stock(cr, uid, month_to, next_month, this.stock_ids, this.category_id.id)
                    return {
                        'type'          : 'ir.actions.report.xml',
                        'report_name'   : 'report_rawmaterial_stock_month',
                        'datas'         : datas,
           }
            else:
                #===================== Lấy dữ liệu báo cáo vàng của nhiều tháng khác nhau=====================
                if res['month_from'] !=False and res['month_to'] != False:
                    month_start = int(res['month_from'])
                    month_end = int(res['month_to'])+1
                    for month in range(month_start,month_end):
                        print 'get data of '+ str(month)
                        month_to = str(this.year_id.name)  +'-'+ str(month)+ '-01'
                        mt_to = datetime.strptime(month_to,'%Y-%m-%d')
                        next_month= str(mt_to+relativedelta.relativedelta( months=1))[:10]
                        key = 'line'+str(month)
                        datas[key] = self.export_rawmaterial_stock(cr, uid, month_to, next_month, this.stock_ids, this.category_id.id)
                        
                    
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'report_rawmaterial_stock',
                'datas'         : datas,
           }
            
        elif res['type_report']=='diamond':
            #============================== REPORT DIAMOND ==================================
            if res['option']=='view':
                #===================== lấy dữ liệu báo cáo diamond của 1 tháng ================================
                if res['month'] != False:
                    month_to = str(this.year_id.name)  +'-'+ res['month']+ '-01'
                    mt_to = datetime.strptime(month_to,'%Y-%m-%d')
                    next_month= str(mt_to+relativedelta.relativedelta( months=1))[:10]
                    
                    datas['line1']  = self.export_diamond_stock(cr, uid, month_to, next_month, this.stock_ids, this.category_id.id)
                    return {
                        'type'          : 'ir.actions.report.xml',
                        'report_name'   : 'report_diamond_stock_sumary_month',
                        'datas'         : datas,
           }  
            else:
                #===================== Lấy dữ liệu báo cáo diamond của nhiều tháng khác nhau=====================
                if res['month_from'] !=False and res['month_to'] != False:
                
                    month_start = int(res['month_from'])
                    month_end = int(res['month_to'])+1
                 
                    for month in range(month_start,month_end):
                        print 'get data of '+ str(month)
                        month_to = str(this.year_id.name)  +'-'+ str(month)+ '-01'
                        mt_to = datetime.strptime(month_to,'%Y-%m-%d')
                        next_month= str(mt_to+relativedelta.relativedelta( months=1))[:10]
                        key = 'line'+str(month)
                        datas[key] = self.export_diamond_stock(cr, uid, month_to, next_month, this.stock_ids, this.category_id.id)     
            
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'report_diamond_stock_sumary',
                'datas'         : datas,
           }             
        
        else:
            
            datas['line'] = self.report_inventory(cr, uid,this.year_id )
            datas['line1'] = self.report_inventory_platinum(cr, uid,this.year_id )
            datas['line2'] = self.report_inventory_diamond(cr, uid,this.year_id )
            
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'hpusa_inventory_report_sumary',
                'datas'         : datas,}
                 
    def export_rawmaterial_stock(self,cr,uid,month_from, next_month,stock_ids,categories):
        arr=[]
        arr.append({
                        'default_code': 'COMPANY STOCK',
                        'name': '-',
                        'uom': '-',
                        'coeff_24k': '-',
                        'qty_24k': '-',
                        'qty_in': '',
                        'qty_first': '-',
                        'qty_out': '-',
                        'qty_lost': '-',
                        'qty_adjust': '-',
                        'end_book': '-',
                        'endbook_24k': '-',
                        'qty_stock':  '-',
                        'stock_24': '-',
                        })  
         
        if stock_ids and categories:
            stock_conf = self.pool.get('hpusa.report.configuration').browse(cr,uid,stock_ids.id)
            stock_id = stock_conf.stock.id
            production_id = stock_conf.production.id
        
            data_main_stock = self.request_stock_report_rawmaterrial(cr, uid, month_from, next_month, stock_id, categories)
            data_production_stock = self.request_stock_report_rawmaterrial(cr, uid, month_from, next_month, production_id, categories)
            weight_loss=0
            if data_main_stock:
                print 'Get main stock success!'
                weight_loss= self.request_loss_month(cr, uid, month_from, next_month)
                arr+=data_main_stock
                max = len(arr)-1
                arr[max]['qty_lost']= weight_loss
                
                
            if data_production_stock:
                arr.append({
                        'default_code': 'PRODUCTION STOCK',
                        'name': '-',
                        'uom': '-',
                        'coeff_24k': '-',
                        'qty_24k': '-',
                        'qty_in': '',
                        'qty_first': '-',
                        'qty_out': '-',
                        'qty_lost': '-',
                        'qty_adjust': '-',
                        'end_book': '-',
                        'endbook_24k': '-',
                        'qty_stock':  '-',
                        'stock_24': '-',
                        })  
                print 'Get production stock success!'
                arr+=data_production_stock
                      
        return arr
    
    def export_diamond_stock(self,cr,uid,month_from, next_month,stock_ids,categories):
        arr=[]
        
        if stock_ids:
            stock_conf = self.pool.get('hpusa.report.configuration').browse(cr,uid,stock_ids.id)
            stock_id = stock_conf.stock.id
            production_id = stock_conf.production.id
        
            data_main_stock = self.request_stock_in_out_diamonds(cr, uid, month_from, next_month, stock_id, categories)
            if data_main_stock:
                print 'Get main stock success!'
                arr=data_main_stock            
        return arr
       
    def report_inventory(self,cr,uid, year_id):
        arr=[]
        
        header=['Tồn Đầu Kỳ',
                'Nhập Trong Kỳ',
                'Xuất Trong Kỳ',
                'TL Đang Thực Hiện Trong Kỳ',
                'TL Hoàn Tất Trong Kỳ',
                'HH Trong Định Mức' ,
                'HH Vượt Định Mức',
                'Trả về USA',
                'TT-24K(Thực tế)',
                'Tồn kho HT-24K(Hệ thống)',
                'TL Chênh Lệch',
                '% Chênh Lệch' ]
        
        description=['Tồn Đầu Kỳ',
                'Nhập = Hàng mua + Ship từ US + Thợ trả về',
                'Xuất = Xuất cho kho sx + xuất cho thợ ',
                'TL Đang Thực Hiện = Tổng trọng lượng thực tế',
                'TL Hoàn Tất Trong Kỳ = Tổng Finished Trong kỳ',
                'HH Trong Định Mức = Tổng trọng lượng định mức từ thợ' ,
                'HH Vượt Định Mức = Tổng trọng lượng vượt định mức thợ',
                'Trả về USA= Tổng trọng lượng thành phẩm của HPUSA + Alexander',
                'Tồn kho 24k (Thực tế) = Tồn kho tổng và tồn kho sx thực tế',
                'Tồn kho 24k HT = Tồn kho hệ thống chưa điều chỉnh',
                'TL Chênh Lệch = Tồn kho 24k (Thực tế) - Tồn kho HT-24K(Hệ thống)',
                '% Chênh Lệch = (Tồn kho 24k (Thực tế) - Tồn kho HT-24K(Hệ thống))/ Tồn kho 24k (Thực tế)' ]
        
        for i in range(0,12):
            value={}
            value ['header']=  header[i]
            value ['description']=  description[i]
            for j in range(1,14):
                key= 'month'+str(j)
                value[key] =''
                
            arr.append(value)   
        
        sum_gold_start = 0
        sum_gold_in = 0 
        sum_gold_out = 0
        sum_gold_pending = 0
        sum_gold_finish = 0
        sum_gold_loss_limit = 0
        sum_gold_loss_over = 0
        sum_gold_ship_to_us  = 0
        sum_gold_end_phyical = 0
        sum_gold_end_erp = 0
        sum_diff_gold = 0
         
        periods=  self.pool.get('hpusa.report.inventory').search(cr,uid,[('year_id','=',year_id.id)])
        if(periods): 
            for period in periods:
                _data=self.pool.get('hpusa.report.inventory').browse(cr,uid,period)
                
                if _data.gold_end_phyical==0:
                    loss_percent =0
                    diff_percent=0
                else:
                    loss_percent =round(float(float(_data.gold_loss *100)/_data.gold_end_phyical or 0.0),3)
                    diff_percent =  round(float(_data.diff_gold*100/_data.gold_end_phyical or 0.0),3)
                    
                key = 'month'+str(int(_data.period))
                arr[0][key] = round(float(_data.gold_start),3)
                arr[1][key] = round(float(_data.gold_in),3) 
                arr[2][key] = round(float(_data.gold_out),3)
                arr[3][key] = round(float(_data.gold_pending),3)
                arr[4][key] = round(float(_data.gold_finish),3)
                arr[5][key] = round(float(_data.gold_loss_limit),3)
                arr[6][key] = round(float(_data.gold_loss_over),3)
                arr[7][key] = round(float(_data.gold_ship_to_us),3)
                arr[8][key] = round(float(_data.gold_end_phyical),3)
                arr[9][key] = round(float(_data.gold_end_erp),3)
                arr[10][key] = round(float(_data.diff_gold),3)
                
                # sum Diffence
                sum_gold_start += round(float(_data.gold_start),3)
                sum_gold_in += round(float(_data.gold_in),3)  
                sum_gold_out +=  round(float(_data.gold_out),3)
                sum_gold_pending += round(float(_data.gold_pending),3)
                sum_gold_finish += round(float(_data.gold_finish),3)
                sum_gold_loss_limit += round(float(_data.gold_loss_limit),3)
                sum_gold_loss_over += round(float(_data.gold_loss_over),3)
                sum_gold_ship_to_us  += round(float(_data.gold_ship_to_us),3)
                sum_gold_end_phyical += round(float(_data.gold_end_phyical),3)
                sum_gold_end_erp += round(float(_data.gold_end_erp),3)
                sum_diff_gold += round(float(_data.diff_gold),3)
        
                if  _data.gold_out>0:
                    arr[11][key] = round(float((_data.diff_gold / _data.gold_out) or 0),3)
            key = 'month13'    
            arr[0][key] = sum_gold_start
            arr[1][key] = sum_gold_in 
            arr[2][key] = sum_gold_out
            arr[3][key] = sum_gold_pending
            arr[4][key] = sum_gold_finish
            arr[5][key] = sum_gold_loss_limit
            arr[6][key] = sum_gold_loss_over
            arr[7][key] = sum_gold_ship_to_us
            arr[8][key] = sum_gold_end_phyical
            arr[9][key] = sum_gold_end_erp
            arr[10][key] = sum_diff_gold
                # calculation total
                
            
        return arr
    
    def report_inventory_platinum(self,cr,uid, year_id):
        arr=[]
        
        header=['Tồn Đầu Kỳ',
                'Nhập Trong Kỳ',
                'Xuất Trong Kỳ',
                'TL Đang Thực Hiện Trong Kỳ',
                'TL Hoàn Tất Trong Kỳ',
                'HH Trong Định Mức' ,
                'HH Vượt Định Mức',
                'Trả về USA',
                'Tồn kho TT-PT950(Hop)',
                'Tồn kho HT-PT950(ERP)',
                'TL Chênh Lệch',
                '% Chênh Lệch' ]
        
        description=['Tồn Đầu Kỳ',
                'Nhập = Hàng mua + Ship từ US + Thợ trả về',
                'Xuất = Xuất cho kho sx + xuất cho thợ ',
                'TL Đang Thực Hiện = Tổng trọng lượng thực tế',
                'TL Hoàn Tất Trong Kỳ = Tổng Finished Trong kỳ',
                'HH Trong Định Mức = Tổng trọng lượng định mức từ thợ' ,
                'HH Vượt Định Mức = Tổng trọng lượng vượt định mức thợ',
                'Trả về USA= Tổng trọng lượng thành phẩm của HPUSA + Alexander',
                'Tồn kho TT-PT950(Hop) = Tồn kho tổng và tồn kho sx thực tế',
                'Tồn kho HT-PT950(ERP) = Tồn kho hệ thống chưa điều chỉnh',
                'TL Chênh Lệch = Tồn kho TT-PT950(Hop) - Tồn kho HT-PT950(ERP)',
                '% Chênh Lệch = (Tồn kho TT-PT950(Hop) - Tồn kho HT-PT950(ERP))/ Tồn kho TT-PT950(Hop)' ]
        
        for i in range(0,12):
            value={}
            value ['header']=  header[i]
            value ['description']=  description[i]
            
            for j in range(1,14):
                key= 'month'+str(j)
                value[key] =''
                
            arr.append(value)   
           
        periods=  self.pool.get('hpusa.report.inventory').search(cr,uid,[('year_id','=',year_id.id)])
        
        sum_pt_start = 0
        sum_pt_in = 0
        sum_pt_out = 0
        sum_pt_pending = 0
        sum_pt_finish = 0
        sum_pt_loss_limit = 0
        sum_pt_loss_over = 0
        sum_pt_ship_to_us = 0
        sum_pt_end_phyical = 0
        sum_pt_end_erp = 0
        sum_diff_pt = 0
 
        if(periods):
                         
            for period in periods:
                _data=self.pool.get('hpusa.report.inventory').browse(cr,uid,period)
                
                if _data.pt_end_phyical==0:
                    loss_percent =0
                    diff_percent=0
                else:
                    loss_percent =round(float(float(_data.pt_loss *100)/_data.pt_end_phyical or 0.0),3)
                    diff_percent =  round(float(_data.pt_loss*100/_data.pt_end_phyical or 0.0),3)
                    
                key = 'month'+str(int(_data.period))
                arr[0][key] = round(float(_data.pt_start),3)
                arr[1][key] = round(float(_data.pt_in),3) 
                arr[2][key] = round(float(_data.pt_out),3)
                arr[3][key] = round(float(_data.pt_pending),3)
                arr[4][key] = round(float(_data.pt_finish),3)
                arr[5][key] = round(float(_data.pt_loss_limit),3)
                arr[6][key] = round(float(_data.pt_loss_over),3)
                arr[7][key] = round(float(_data.pt_ship_to_us),3)
                arr[8][key] = round(float(_data.pt_end_phyical),3)
                arr[9][key] = round(float(_data.pt_end_erp),3)
                arr[10][key] = round(float(_data.diff_pt),3)
                arr[11][key] = diff_percent
                
                sum_pt_start += round(float(_data.pt_start),3)
                sum_pt_in += round(float(_data.pt_in),3) 
                sum_pt_out += round(float(_data.pt_out),3)
                sum_pt_pending += round(float(_data.pt_pending),3)
                sum_pt_finish += round(float(_data.pt_finish),3)
                sum_pt_loss_limit += round(float(_data.pt_loss_limit),3)
                sum_pt_loss_over += round(float(_data.pt_loss_over),3)
                sum_pt_ship_to_us += round(float(_data.pt_ship_to_us),3)
                sum_pt_end_phyical += round(float(_data.pt_end_phyical),3)
                sum_pt_end_erp += round(float(_data.pt_end_erp),3)
                sum_diff_pt +=  round(float(_data.diff_pt),3)   
        
        key = 'month13'
        
        sum_pt_start = 0
        sum_pt_in = 0
        sum_pt_out = 0
        sum_pt_pending = 0
        sum_pt_finish = 0
        sum_pt_loss_limit = 0
        sum_pt_loss_over = 0
        sum_pt_ship_to_us = 0
        sum_pt_end_phyical = 0
        sum_pt_end_erp = 0
        sum_diff_pt = 0
        
        arr[0][key] = sum_pt_start
        arr[1][key] = sum_pt_in
        arr[2][key] = sum_pt_out
        arr[3][key] = sum_pt_pending
        arr[4][key] = sum_pt_finish
        arr[5][key] = sum_pt_loss_limit
        arr[6][key] = sum_pt_loss_over
        arr[7][key] = sum_pt_ship_to_us
        arr[8][key] = sum_pt_end_phyical
        arr[9][key] = sum_pt_end_erp
        arr[10][key] = sum_diff_pt
                 
                # calculation total
        return arr
    
    def report_inventory_diamond(self,cr,uid, year_id):
        arr=[]
        
        header=['Tồn Đầu Kỳ',
                'Nhập Trong Kỳ',
                'Xuất Trong Kỳ',
                'TL Đang Thực Hiện Trong Kỳ',
                'TL Hoàn Tất Trong Kỳ',
                'HH Trong Định Mức' ,
                'HH Vượt Định Mức',
                'Trả về USA',
                'Tồn kho TT-Dia(Hop)',
                'Tồn kho HT-Dia(ERP)',
                'TL Chênh Lệch',
                '% Chênh Lệch' ]
        
        description=['Tồn Đầu Kỳ',
                'Nhập = Hàng mua + Ship từ US + Thợ trả về',
                'Xuất = Xuất cho kho sx + xuất cho thợ ',
                'TL Đang Thực Hiện = Tổng trọng lượng thực tế',
                'TL Hoàn Tất Trong Kỳ = Tổng Finished Trong kỳ',
                'HH Trong Định Mức = Tổng trọng lượng định mức từ thợ' ,
                'HH Vượt Định Mức = Tổng trọng lượng vượt định mức thợ',
                'Trả về USA= Tổng trọng lượng thành phẩm của HPUSA + Alexander',
                'Tồn kho TT(Hop) = Tồn kho tổng và tồn kho sx thực tế',
                'Tồn kho HT = Tồn kho hệ thống chưa điều chỉnh',
                'TL Chênh Lệch = Tồn kho TT(Hop) - Tồn kho HT(ERP)',
                '% Chênh Lệch = (Tồn kho TT(Hop) - Tồn kho HT(ERP))/ Tồn kho TT(Hop)' ]
        
        for i in range(0,12):
            value={}
            value ['header']=  header[i]
            value ['description']=  description[i]
            for j in range(1,14):
                key= 'month'+str(j)
                value[key] =''
                
            arr.append(value)   
        
        
        sum_diamond_start = 0
        sum_diamond_in= 0
        sum_diamond_out = 0
        sum_diamond_pending = 0
        sum_diamond_finish = 0
        sum_diamond_loss_limit = 0
        sum_diamond_loss_over = 0
        sum_diamond_ship_to_us = 0 
        sum_diamond_end_physical = 0
        sum_diamond_end_erp = 0
        sum_diff_diamond = 0
           
        periods=  self.pool.get('hpusa.report.inventory').search(cr,uid,[('year_id','=',year_id.id)])
        if(periods): 
            for period in periods:
                _data=self.pool.get('hpusa.report.inventory').browse(cr,uid,period)
                
                if _data.diamond_end_physical==0:
                  
                    diff_percent=0
                else:
                    
                    diff_percent =  round(float(_data.diamond_loss*100/_data.diamond_end_physical or 0.0),3)
                    
                key = 'month'+str(int(_data.period))
                arr[0][key] = round(float(_data.diamond_start),3)
                arr[1][key] = round(float(_data.diamond_in),3) 
                arr[2][key] = round(float(_data.diamond_out),3)
                arr[3][key] = round(float(_data.diamond_pending),3)
                arr[4][key] = round(float(_data.diamond_finish),3)
                arr[5][key] = round(float(_data.diamond_loss_limit),3)
                arr[6][key] = round(float(_data.diamond_loss_over),3)
                arr[7][key] = round(float(_data.diamond_ship_to_us),3)
                arr[8][key] = round(float(_data.diamond_end_physical),3)
                arr[9][key] = round(float(_data.diamond_end_erp),3)
                arr[10][key] = round(float(_data.diff_diamond),3)
                arr[11][key] = diff_percent  
                  
                # calculation total
                sum_diamond_start = round(float(_data.diamond_start),3)
                sum_diamond_in += round(float(_data.diamond_in),3)
                sum_diamond_out += round(float(_data.diamond_out),3)
                sum_diamond_pending += round(float(_data.diamond_pending),3)
                sum_diamond_finish += round(float(_data.diamond_finish),3)
                sum_diamond_loss_limit += round(float(_data.diamond_loss_limit),3)
                sum_diamond_loss_over += round(float(_data.diamond_loss_over),3)
                sum_diamond_ship_to_us += round(float(_data.diamond_ship_to_us),3) 
                sum_diamond_end_physical += round(float(_data.diamond_end_physical),3)
                sum_diamond_end_erp += round(float(_data.diamond_end_erp),3)
                sum_diff_diamond += round(float(_data.diff_diamond),3)
                
        key='month13'        
        arr[0][key] = sum_diamond_start
        arr[1][key] = sum_diamond_in
        arr[2][key] = sum_diamond_out
        arr[3][key] = sum_diamond_pending
        arr[4][key] = sum_diamond_finish
        arr[5][key] = sum_diamond_loss_limit
        arr[6][key] = sum_diamond_loss_over
        arr[7][key] = sum_diamond_ship_to_us
        arr[8][key] = sum_diamond_end_physical
        arr[9][key] = sum_diamond_end_erp
        arr[10][key] = sum_diff_diamond
                   
            
        return arr
    
    def view_report(self, cr, uid, ids, context=None):
        
        this = self.browse(cr, uid,ids,context =None)[0]
        stock_id = 0
        production_id = 0
        category = 0
        year_id = this.year_id.name
        
        if this.stock_ids:
            stock_id = this.stock_ids.stock.id
            production_id = this.stock_ids.production.id
        if this.category_id:
            category = this.category_id.id
        stock_data = []
        production_data=[]
        index= 0
        html =''
        if int(this.month_from) and int(this.month_to):
            for k in range (int(this.month_from) ,int(this.month_to)):
                
                month_to = str(year_id)  +'-'+ str(k)+ '-01'
                mt_to = datetime.strptime(month_to,'%Y-%m-%d')
                next_month= str(mt_to+relativedelta.relativedelta( months=1))[:10]
                stock = self.request_stock_report_rawmaterrial(cr, uid, month_to, next_month, stock_id, category)
                #Du Lieu Kho Nguon Theo Thang 
                stock_data.append({'month': k,
                                    'data': stock,
                                    })
                production = self.request_stock_report_rawmaterrial(cr, uid, month_to, next_month, production_id, category)
                 #Du Lieu Kho San Xuat Theo Thang 
                production_data.append({'month': k,
                                        'data': production,
                                    })
                
        self.write(cr, uid,ids, {'state': 'get',
                                    'context':html }, context=context)
        return  {
             'type': 'ir.actions.act_window',
             'res_model': 'wizard.hpusa.warehouse.report',
             'view_mode': 'form',
             'view_type': 'form',
             'res_id':this.id,
             'views': [(False, 'form')],
             'target': 'new',}
                
    def view_report_month(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid,ids,context =None)[0]
        
        html = ''
        
        if(this.type_report=='general'):
            inventory_data = self.report_inventory(cr, uid,this.year_id )
            inventory_platinum = self.report_inventory_platinum(cr, uid,this.year_id)
            inventory_diamond = self.report_inventory_diamond(cr, uid, this.year_id)
            html+= self.create_html_inventory_report(cr, uid, this.year_id.name, inventory_data,inventory_platinum,inventory_diamond)
            
        else:
                
            stock_id = 0
            production_id = 0
            category = 0
            year_id = int(this.year_id.name)
            
            if this.month !=False:
                month  =    str(year_id) +'-'+ str(this.month)+ '-01'
                mt = datetime.strptime(month,'%Y-%m-%d')
                first_of_next_month = str(mt+relativedelta.relativedelta( months=1))[:10]
                #last_of_this_month = str(first_of_next_month - relativedelta.relativedelta( days=1))[:10]
                if this.stock_ids:
                    stock_id = this.stock_ids.stock.id
                    production_id = this.stock_ids.production.id
                if this.category_id:
                    category = this.category_id.id
                stock_data = []
                stock_data = self.request_stock_report_rawmaterrial(cr, uid, month, first_of_next_month, stock_id, category)
                
                if stock_data:
                    stock_name= 'KHO TỔNG'
                    weight_loss= self.request_loss_month(cr, uid, month, first_of_next_month)
                    max = len(stock_data)-1
                    stock_data[max]['qty_lost']= weight_loss
                
                    html+= self.create_html_raw(cr, uid, this.month, stock_data,stock_name)
                    
                production_data=[]
                production_data = self.request_stock_report_rawmaterrial(cr, uid, month, first_of_next_month, production_id, category)
                
                if production_data:
                    stock_name="KHO SẢN XUẤT"
                    html+= self.create_html_raw(cr, uid, this.month, production_data,stock_name)    
        self.write(cr, uid,ids, {'state': 'get',
                                    'context':html }, context=context)
        return  {
             'type': 'ir.actions.act_window',
             'res_model': 'wizard.hpusa.warehouse.report',
             'view_mode': 'form',
             'view_type': 'form',
             'res_id':this.id,
             'views': [(False, 'form')],
             'target': 'new',
                }

    def update_data(self,cr,uid,ids,context):
        
        
        return True
    
    def request_loss_month(self,cr,uid,date_from,date_to):
        weight_loss= 0
        
        sql = '''
                select sum(loss_weight) as loss
                from mrp_production
                where   mo_date >= to_date('%s','YYYY-MM-DD') 
                AND mo_date < to_date('%s','YYYY-MM-DD')   
            '''%( date_from, date_to)
            
        cr.execute(sql)
        print sql
        results = cr.dictfetchall()
        if len(results)>=1:
            for result in results:
                if(result['loss']!=None):
                    weight_loss= float(result['loss'])
        
        return  weight_loss

    def create_html_inventory_report(self,cr,uid,year,inventory_data,inventory_platinum,inventory_diamond):
        html=''
        if inventory_data:
            html +='<span contenteditable="false">'\
                    '<h1  style = "text-align:center"> BÁO CÁO TỔNG HỢP TỒN KHO NĂM '+year+'</h1>'\
                    '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                    '<thead class = "theads">'\
                    '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                    '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">MONTH</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">JANUARY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >FEBURARY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >MARCH</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >APRIL</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >MAY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >JUNE</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >JULY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >AUGUST</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >SEPTEMBER</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >OCTOBER</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >NOVEMBER</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >DECCEMBER</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Total</th>'\
                    '</tr>'\
                    '</thead>'\
                    '<tbody>'
            for i in inventory_data:
                    html += '<tr class = "trs">'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['header'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month1'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month2'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month3'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month4'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month5'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month6'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month7'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month8'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month9'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month10'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month11'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month12'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month13'])+'</td>'\
                            '</tr>'
            if inventory_platinum:
                html +=  '<tr class = "trs"><td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center"> Platinum</td></tr>'    
                for i in inventory_platinum:
                   
                    html+='<tr class = "trs">'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['header'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month1'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month2'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month3'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month4'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month5'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month6'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month7'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month8'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month9'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month10'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month11'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month12'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month13'])+'</td>'\
                            '</tr>'
            if   inventory_diamond:
                html += '<tr class = "trs"><td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center"> Diamond</td></tr>'  
                for i in inventory_diamond:
                   
                    html+= '<tr class = "trs">'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['header'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month1'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month2'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month3'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month4'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month5'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month6'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month7'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month8'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month9'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month10'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month11'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month12'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['month13'])+'</td>'\
                            '</tr>'
            html += '</tbody>'\
                        '</table>'\
                        '</span>'
        else :
            html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BÁO CÁO TỔNG HỢP TỒN KHO CUỐI KỲ NĂM'+year+'</h1>'\
                    '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                    '<thead class = "theads">'\
                    '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                    '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white">MONTH</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">JANUARY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >FEBURARY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >MARCH</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >APRIL</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >MAY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >JUNE</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >JULY</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >AUGUST</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >SEPTEMBER</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >OCTOBER</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >NOVEMBER</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >DECCEMBER</th>'\
                    '</tr>'\
                    '</thead>'\
                    '<tbody>'\
                    '</tbody>'\
                    '</table>'\
                    '</span>'
        return html
        
        
        return html

    def create_html_raw(self,cr,uid,month,stock_data,stock_name):
        html=''
        if stock_data:
            html +='<span contenteditable="false">'\
                    '<h1  style = "text-align:center"> BÁO CÁO NHẬP XUẤT TỒN '+stock_name+' THÁNG '+month+'</h1>'\
                    '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                    '<thead class = "theads">'\
                    '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                    '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">MÃ HÀNG HÓA</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">TÊN HÀNG HÓA</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. ĐẦU KỲ(gr)</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >ĐẦU KỲ 24K (gr)</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. NHẬP</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. XUẤT</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >HAO HỤT</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. CUỐI KỲ</th>'\
                    '<th  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">CUỐI KỲ 24K(gr)</th>'\
                    '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Ghi Chú</th>'\
                    '</tr>'\
                    '</thead>'\
                    '<tbody>'
            for i in stock_data:
                    html += '<tr class = "trs">'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['default_code'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ i['name']+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['qty_first'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['qty_24k'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['qty_in'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['qty_out'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['qty_lost'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['qty_stock'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['stock_24'])+'</td>'\
                            '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center"></td>'\
                            '</tr>'
            html += '</tbody>'\
                        '</table>'\
                        '</span>'
        else :
            html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BÁO CÁO NHẬP XUẤT TỒN '+stock_name+' THÁNG '+month+' </h1>'\
                '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                '<thead class = "theads">'\
                '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">MÃ HÀNG HÓA</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">TÊN HÀNG HÓA</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. ĐẦU KỲ(gr)</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >ĐẦU KỲ 24K (gr)</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. NHẬP</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. XUẤT</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >HAO HỤT</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL. CUỐI KỲ</th>'\
                '<th  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">CUỐI KỲ 24K(gr)</th>'\
                '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Ghi Chú</th>'\
                '</tr>'\
                '</thead>'\
                '<tbody>'\
                '</tbody>'\
                '</table>'\
                '</span>'
        return html
         
    def request_stock_report_rawmaterrial(self, cr, uid, date_from, date_to, location_id, category):
        str_query = ''
        if category:
            str_query += '''WHERE cate.id = %s'''%(category)
            
        sql = '''
                SELECT p.id, MAX(pt.list_price) as list_price
                , p.default_code
                , p.name_template as name
                , uom.name as uom
                , coalesce(p.coeff_24k,0) as coeff_24k
                , coalesce(MAX(tab.qty),0) as qty_first
                , coalesce(MAX(tab.qty),0)* coalesce(p.coeff_24k,0) as qty_24k
                , coalesce(MAX(tab2.qty),0)  as qty_in                 
                , coalesce(MAX(tab3.qty),0) as qty_out
                , coalesce(MAX(tab4.qty),0) as qty_lost
                , coalesce(MAX(tab_adjust.qty),0)* coalesce(p.coeff_24k,0) as qty_adjust_24k
                , coalesce(MAX(tab_adjust.qty),0) as qty_adjust
                , coalesce(MAX(tab.qty),0)  + coalesce(MAX(tab2.qty),0) - coalesce(MAX(tab_adjust.qty),0) -coalesce(MAX(tab3.qty),0)  as end_book
                , (coalesce(MAX(tab.qty),0)  + coalesce(MAX(tab2.qty),0)  - coalesce(MAX(tab_adjust.qty),0) -coalesce(MAX(tab3.qty),0))*coalesce(p.coeff_24k,0) as endbook_24k
                , coalesce(MAX(tab.qty),0) + coalesce(MAX(tab2.qty),0)  -coalesce(MAX(tab3.qty),0) as qty_real
                , (coalesce(MAX(tab.qty),0) + coalesce(MAX(tab2.qty),0)  -coalesce(MAX(tab3.qty),0)) *coalesce(p.coeff_24k,0) as real_24k
                    FROM product_product p
                    -- Dau Ky
                    LEFT JOIN
                            (
                            SELECT product_id, SUM(qty) as qty FROM
                                (
                                SELECT product_id, coalesce(-SUM(product_qty),0) as qty
                                FROM stock_move WHERE location_id = %s
                                AND date < '%s' 
                                AND state = 'done'
                                AND location_id <>  location_dest_id
                                GROUP BY product_id
                                UNION ALL
                                SELECT product_id, coalesce(SUM(product_qty),0) as qty
                                FROM stock_move
                                WHERE location_dest_id = %s
                                AND location_id <>  location_dest_id
                                AND date < '%s'
                                AND state = 'done'
                                GROUP BY product_id
                                ) as first
                                GROUP BY product_id
                        ) as tab ON(tab.product_id = p.id)

                    -- Nhap
                    LEFT JOIN (
                        SELECT product_id, coalesce(SUM(product_qty),0) as qty
                        FROM stock_move
                        WHERE location_dest_id = %s
                        AND date >= '%s'
                        AND date <= '%s'
                        AND state = 'done'
                        AND location_id <>  location_dest_id
                        GROUP BY product_id
                        ) as tab2 ON(tab2.product_id =  p.id)

                    -- Xuat
                    LEFT JOIN (
                        SELECT product_id, coalesce(SUM(product_qty),0) as qty FROM stock_move WHERE location_id = %s AND date >= '%s' AND date <= '%s'  AND state = 'done' AND location_id <>  location_dest_id
                        GROUP BY product_id
                    ) as tab3 ON(tab3.product_id =  p.id)

                    -- Hu
                    LEFT JOIN (
                        SELECT product_id, coalesce(SUM(product_qty),0) as qty
                        FROM stock_move sm
                        LEFT JOIN stock_picking sp ON(sp.id = sm.picking_id)
                        WHERE sm.location_id = %s 
                        AND sm.date >= '%s' 
                        AND sm.date <= '%s'  
                        AND sm.state = 'done' 
                        AND sm.location_id <>  sm.location_dest_id 
                        AND sp.hp_transfer_type = 'lost'
                        GROUP BY product_id
                    ) as tab4 ON(tab4.product_id =  p.id)
                    
                    --- adjust 
            left join 
            (
                       select adjust.product_id, sum(adjust.qty) as qty, sum (adjust.wt) as wt
                       from(
                            SELECT product_id
                            , coalesce(-SUM(product_qty),0) as qty
                            ,coalesce(-SUM(weight_mo),0) as wt
                            FROM stock_move sm
                            , stock_picking sp 
                            WHERE sp.id = sm.picking_id
                            AND sm.location_id = %s
                            AND sm.date >= '%s'
                            AND sm.date <= '%s'
                            AND sm.state = 'done'
                            AND sm.location_id <>  sm.location_dest_id
                            AND sp.hp_transfer_type = 'adjust'
                            GROUP BY product_id
                union all
                        --- adjust 
                            SELECT product_id
                            , coalesce( SUM(product_qty),0) as qty
                            ,coalesce(SUM(weight_mo),0) as wt
                            FROM stock_move sm
                            , stock_picking sp 
                            WHERE sp.id = sm.picking_id
                            AND sm.location_dest_id = %s
                            AND sm.date >= '%s'
                            AND sm.date <= '%s'
                            AND sm.state = 'done'
                            AND sm.location_id <>  sm.location_dest_id
                            AND sp.hp_transfer_type = 'adjust'
                            GROUP BY product_id
                ) as adjust group by product_id
            ) as tab_adjust ON(tab_adjust.product_id =  p.id)

                    LEFT JOIN product_template pt ON(pt.id = p.product_tmpl_id)
                    LEFT JOIN product_uom uom ON(uom.id = pt.uom_id)
                    LEFT JOIN product_category cate ON (cate.id = pt.categ_id)
                    %s
                    GROUP BY p.id, p.default_code, pt.name, uom.name
                    HAVING ABS(coalesce(SUM(tab.qty),0)) + ABS(coalesce(SUM(tab2.qty),0)) + ABS(coalesce(SUM(tab3.qty),0))  <> 0
            Order by  p.default_code, pt.name, uom.name
            '''%(location_id, date_from,location_id, date_from, location_id, date_from, date_to, location_id, date_from, date_to, location_id, date_from, date_to,location_id, date_from, date_to,location_id, date_from, date_to, str_query)
        cr.execute(sql)
        print sql
        result = cr.dictfetchall()
        arr = []

        sum_qty_first=0
        sum_qty_24k=0
        sum_qty_in =0
        sumqty_out=0
        sumqty_loss=0
        sum_qty_adjust=0
        sum_qty_adjust_24k=0
        sum_qty_book=0
        sum_qty_book24k=0
        sum_qty_real=0
        sumqty_real_24k=0
    
        for item in result:
#             if float(item['qty_adjust']>=0):
#                 qty_in = item['qty_in']+item['qty_adjust']
#                 qty_out =item['qty_out']
#             else:
#                 qty_out =  item['qty_out'] +item['qty_adjust']   
#                 qty_in = item['qty_in']
                
            arr.append({
                        'default_code': item['default_code'],
                        'name': item['name'],
                        'uom': item['uom'],
                        'coeff_24k': item['coeff_24k'],
                        'qty_first': item['qty_first'],
                        'qty_24k': item['qty_24k'],
                        'qty_in': item['qty_in'],
                        'qty_out': item['qty_out'],
                        'qty_lost': item['qty_lost'],
                        'qty_adjust': item['qty_adjust'],
                        'qty_adjust_24k': round(float(item['qty_adjust_24k'] or 0.0),2) ,
                        'end_book': item['end_book'],
                        'endbook_24k': item['endbook_24k'],
                        'qty_stock': item['qty_real'],
                        'stock_24':  item['real_24k'],
                        })
            # hpusa 13-07-2015
            sum_qty_first+= item['qty_first']
            sum_qty_24k += item['qty_24k']
            sum_qty_in +=item['qty_in']
            sumqty_out +=item['qty_out']
            sumqty_loss += item['qty_lost']
            sum_qty_adjust +=item['qty_adjust']
            sum_qty_adjust_24k+= round(float(item['qty_adjust_24k'] or 0.0),2)
            sum_qty_book +=item['end_book']
            sum_qty_book24k +=item['endbook_24k']
            sum_qty_real +=item['qty_real']
            sumqty_real_24k +=item['real_24k']


        arr.append({
                        'default_code': 'Total',
                        'name': ' ',
                        'uom': '',
                        'coeff_24k': '',
                        'qty_first': round(sum_qty_first,2),
                        'qty_24k':round(sum_qty_24k,2),
                        'qty_in': round(sum_qty_in,2),
                        'qty_out': round(sumqty_out,2),
                        'qty_lost': round(sumqty_loss,2) ,
                        'qty_adjust': round(sum_qty_adjust,2),
                        'qty_adjust_24k': round(sum_qty_adjust_24k,2),
                        'end_book': round(sum_qty_book,2),
                        'endbook_24k': round(sum_qty_book24k,2),
                        'qty_stock': round(sum_qty_real,2),
                        'stock_24':  round(sumqty_real_24k,2),
                        })
        # hpusa 13-07-2015

        return arr
    
    def request_stock_in_out_diamonds(self, cr, uid, date_from, date_to, location_id, category):
        print 'Start get information'
        cate_arr=[]
        cate_arr.append(category)
        #===================get array Categories ids===============
        for i in range(0,5):
            for cate in cate_arr:
                categories = self.pool.get('product.category').search(cr, uid, [('parent_id','=',cate)], context=None)
                if categories:
                    for item in categories:
                        if item not in cate_arr:
                            cate_arr.append(item)
                    
        
        total_qty_in = 0
        total_wt_in = 0
        total_qty_first = 0
        total_wt_first = 0
        total_qty_out = 0
        total_wt_out = 0
        total_qty_lost = 0
        total_wt_lost = 0
        total_qty_ship = 0
        total_wt_ship = 0
        total_qty_endbook = 0
        total_wt_endbook = 0
        total_qty_stock = 0
        total_wt_stock = 0
        total_qty_adjust = 0
        total_wt_adjust = 0
        
        arr = []
        for cate in cate_arr:
            
            str_query = ''
            if cate:
                str_query += '''WHERE cate.id = %s'''%(cate)
            #hpusa 13-07-2015    
            sql = '''
                    SELECT p.id
                        , MAX(pt.list_price) as list_price
                        , p.default_code
                        , p.name_template as name
                        , qlty.name as quality
                        , qlty.description as quality_description
                        , uom.name as uom
                        , coalesce(MAX(tab.qty),0) as qty_first
                        , coalesce(MAX(tab.wt),0) as wt_first
                        , coalesce(MAX(tab2.qty),0) as qty_in 
                        , coalesce(MAX(tab2.wt),0) as wt_in
                        , coalesce(MAX(tab3.qty),0) as qty_out
                        , coalesce(MAX(tab3.wt),0) as wt_out
                        , coalesce(MAX(tab4.qty),0) as qty_lost
                        , coalesce(MAX(tab4.wt),0) as wt_lost
                        , coalesce(MAX(tab5.qty),0) as qty_ship
                        , coalesce(MAX(tab5.wt),0) as wt_ship
                        , coalesce(MAX(tab_adjust.qty),0) as qty_adjust
                        , coalesce(MAX(tab_adjust.wt),0) as wt_adjust
                        FROM product_product p
                         -- quality category
                         LEFT JOIN
                                (
                                SELECT id, name , description
                                from product_quality_categories   
                            ) as qlty ON(qlty.id = p.product_quality_id)
                            
                        -- Dau Ky
                        LEFT JOIN
                                (
                                SELECT product_id, SUM(qty) as qty, sum(wt) as wt FROM
                                    (
                                    SELECT product_id
                                    , coalesce(-SUM(product_qty),0) as qty
                                    , coalesce(-SUM(weight_mo),0) as wt
                                    FROM stock_move
                                    WHERE location_id = %s
                                    AND date < '%s'
                                    AND state = 'done'
                                    AND location_id <>  location_dest_id
                                    GROUP BY product_id
                                    UNION ALL
                                    SELECT product_id
                                    , coalesce(SUM(product_qty),0) as qty
                                    ,coalesce(SUM(weight_mo),0) as wt
                                    FROM stock_move
                                    WHERE location_dest_id = %s
                                    AND date < '%s'
                                    AND location_id <>  location_dest_id
                                    AND state = 'done'
                                    GROUP BY product_id
                                    ) as first
                                    GROUP BY product_id
                            ) as tab ON(tab.product_id = p.id)

                        -- Nhap
                        LEFT JOIN (
                            SELECT _second.product_id, SUM(_second.qty) as qty, sum(_second.wt) as wt FROM
                            
                            (
                            SELECT product_id
                            , coalesce(SUM(product_qty),0) as qty
                            ,coalesce(SUM(weight_mo),0) as wt
                            FROM stock_move
                            WHERE location_dest_id = %s
                            AND date >= '%s'
                            AND date <= '%s' AND state = 'done'
                            AND location_id <>  location_dest_id
                            GROUP BY product_id
                            UNION ALL
                            SELECT product_id
                            , coalesce(-SUM(product_qty),0) as qty
                            ,coalesce(-SUM(weight_mo),0) as wt
                            FROM stock_move sm
                            LEFT JOIN stock_picking sp ON(sp.id = sm.picking_id)
                            WHERE sm.location_dest_id = %s
                            AND sm.date >= '%s'
                            AND sm.date <= '%s'
                            AND sm.state = 'done'
                            AND sm.location_id <>  sm.location_dest_id
                            AND sp.hp_transfer_type = 'return'
                            GROUP BY product_id
                            ) as _second
                            GROUP BY product_id
                            
                            ) as tab2 ON(tab2.product_id =  p.id)

                        -- Xuat
                        LEFT JOIN (
                            SELECT _third.product_id as product_id, SUM(_third.qty) as qty, sum(_third.wt) as wt FROM(
                            SELECT product_id
                            , coalesce(SUM(product_qty),0) as qty
                            ,coalesce(SUM(weight_mo),0) as wt
                            FROM stock_move
                            WHERE location_id = %s
                            AND date >= '%s'
                            AND date <= '%s'
                            AND state = 'done'
                            AND location_id <>  location_dest_id
                            GROUP BY product_id
                            UNION ALL
                             SELECT product_id
                            , coalesce(-SUM(product_qty),0) as qty
                            ,coalesce(-SUM(weight_mo),0) as wt
                            FROM stock_move sm
                            LEFT JOIN stock_picking sp ON(sp.id = sm.picking_id)
                            WHERE sm.location_dest_id = %s
                            AND sm.date >= '%s'
                            AND sm.date <= '%s'
                            AND sm.state = 'done'
                            AND sm.location_id <>  sm.location_dest_id
                            AND sp.hp_transfer_type = 'return'
                            GROUP BY product_id
                            )as _third
                            GROUP BY product_id
                        ) as tab3 ON(tab3.product_id =  p.id)

                        -- Hu
                        LEFT JOIN (
                            SELECT product_id
                            , coalesce(SUM(product_qty),0) as qty
                            ,coalesce(SUM(weight_mo),0) as wt
                            FROM stock_move sm
                            LEFT JOIN stock_picking sp ON(sp.id = sm.picking_id)
                            WHERE sm.location_id = %s
                            AND sm.date >= '%s'
                            AND sm.date <= '%s'
                            AND sm.state = 'done'
                            AND sm.location_id <>  sm.location_dest_id
                            AND sp.hp_transfer_type = 'lost'
                            GROUP BY product_id
                        ) as tab4 ON(tab4.product_id =  p.id)

                        -- Shipping
                        LEFT JOIN (
                            SELECT product_id
                            , coalesce(SUM(product_qty),0) as qty
                            ,coalesce(SUM(weight_mo),0) as wt
                            FROM stock_move sm
                            , stock_picking sp 
                            WHERE sp.id = sm.picking_id
                            AND sm.location_id = %s
                            AND sm.date >= '%s'
                            AND sm.date <= '%s'
                            AND sm.state = 'done'
                            AND sm.location_id <>  sm.location_dest_id
                            AND sp.hp_transfer_type = 'ship'
                            GROUP BY product_id
                        ) as tab5 ON(tab5.product_id =  p.id)
                        
                         --- adjust 
                        left join 
                        (
                                   select adjust.product_id, sum(adjust.qty) as qty, sum (adjust.wt) as wt
                                   from(
                                        SELECT product_id
                                        , coalesce(-SUM(product_qty),0) as qty
                                        ,coalesce(-SUM(weight_mo),0) as wt
                                        FROM stock_move sm
                                        , stock_picking sp 
                                        WHERE sp.id = sm.picking_id
                                        AND sm.location_id = %s
                                        AND sm.date >= '%s'
                                        AND sm.date <= '%s'
                                        AND sm.state = 'done'
                                        AND sm.location_id <>  sm.location_dest_id
                                        AND sp.hp_transfer_type = 'adjust'
                                        GROUP BY product_id
                            union all
                                    --- adjust 
                                        SELECT product_id
                                        , coalesce( SUM(product_qty),0) as qty
                                        ,coalesce(SUM(weight_mo),0) as wt
                                        FROM stock_move sm
                                        , stock_picking sp 
                                        WHERE sp.id = sm.picking_id
                                        AND sm.location_dest_id = %s
                                        AND sm.date >= '%s'
                                        AND sm.date <= '%s'
                                        AND sm.state = 'done'
                                        AND sm.location_id <>  sm.location_dest_id
                                        AND sp.hp_transfer_type = 'adjust'
                                        GROUP BY product_id
                            ) as adjust group by product_id
                        ) as tab_adjust ON(tab_adjust.product_id =  p.id)

                        LEFT JOIN product_template pt ON(pt.id = p.product_tmpl_id)
                        LEFT JOIN product_uom uom ON(uom.id = pt.uom_id)
                        LEFT JOIN product_category cate ON (cate.id = pt.categ_id)
                        %s
                        GROUP BY p.id, p.default_code, pt.name, uom.name,qlty.name ,qlty.description
                        HAVING ABS(coalesce(SUM(tab.qty),0)) + ABS(coalesce(SUM(tab2.qty),0)) + ABS(coalesce(SUM(tab3.qty),0))  <> 0
                Order by  p.default_code, pt.name, uom.name
                '''%(location_id, date_from,location_id, date_from, location_id, date_from, date_to, location_id, date_from, date_to, location_id,date_from, date_to, location_id,date_from, date_to, location_id, date_from, date_to,location_id, date_from, date_to,location_id, date_from, date_to,location_id, date_from, date_to, str_query)
            cr.execute(sql)
            print sql
            result = cr.dictfetchall() 
           
     
        # hpusa 13-07-2015
            sum_qty_first=0
            sum_wt_first=0
            sum_qty_in=0
            sum_wt_in=0
            sum_qty_out=0
            sum_wt_out=0
            sum_qty_lost=0
            sum_wt_lost=0
            sum_qty_ship=0
            sum_wt_ship=0
            sum_qty_book=0
            sum_wt_book=0
            sum_qty_stock=0
            sum_wt_stock=0
            sum_qty_adjust=0
            sum_wt_adjust=0
            
            #================ Print product categories name 
            cate = self.pool.get('product.category').browse(cr,uid,cate,context=None)
            if len(result)>=1:
                arr.append({
                                'default_code': '-',
                                'name': cate.name,
                                'quality':'-',
                                'quality_description':'-',       
                                'qty_in': '-',
                                'wt_in': '-',
                                'qty_first': '-',
                                'wt_first': '-',
                                'qty_out': '-',
                                'wt_out': '-',
                                'qty_lost': '-',
                                'wt_lost': '-',
                                'qty_ship': '-',
                                'wt_ship': '-',
                                'qty_adjust':  '-',
                                'wt_adjust':  '-',
                                'qty_stock':  '-',
                                'wt_stock':  '-',
                                'qty_endbook':  '-',
                                'wt_endbook':  '-',
                                })
    
            for item in result:
                if float(item['qty_adjust']>=0):
                    qty_in = item['qty_in']-item['qty_adjust']
                    wt_in= item['wt_in']-item['wt_adjust']
                    qty_out =item['qty_out']
                    wt_out =item['wt_out']
                else:
                    qty_in = item['qty_in']
                    wt_in= item['wt_in']
                    qty_out =item['qty_out']-item['qty_adjust']
                    wt_out =item['wt_out']-item['wt_adjust']
                
                arr.append({
                            'default_code': item['default_code'],
                            'name': item['name'],
                            'quality': item['quality'],
                            'quality_description': item['quality_description'],
                            'qty_in': qty_in,
                            'wt_in': wt_in,
                            'qty_first': item['qty_first'],
                            'wt_first': item['wt_first'],
                            'qty_out': qty_out,
                            'wt_out': wt_out,
                            'qty_lost': item['qty_lost'],
                            'wt_lost': item['wt_lost'],
                            'qty_ship': item['qty_ship'],
                            'wt_ship': item['wt_ship'],
                            'qty_adjust': item['qty_adjust'],
                            'wt_adjust': item['wt_adjust'],
                            'qty_stock':  item['qty_first'] + item['qty_in'] - item['qty_out'] ,
                            'wt_stock':  item['wt_first'] + item['wt_in'] - item['wt_out'] ,
                            'qty_endbook':item['qty_first'] + qty_in -qty_out ,
                            'wt_endbook':item['wt_first'] + wt_in - wt_out ,
                            })
         # hpusa 13-07-2015
                sum_qty_first +=item['qty_first']
                sum_wt_first+=item['wt_first']
                sum_qty_in +=qty_in
                sum_wt_in +=wt_in
                sum_qty_out +=qty_out
                sum_wt_out +=wt_out
                sum_qty_lost +=item['qty_lost']
                sum_wt_lost +=item['wt_lost']
                sum_qty_ship +=item['qty_ship']
                sum_wt_ship +=item['wt_ship']
                sum_qty_stock += (item['qty_first']  + item['qty_in'] - item['qty_out'])
                sum_wt_stock += (item['wt_first'] + item['wt_in']  - item['wt_out'])
                sum_qty_adjust+= item['qty_adjust']
                sum_wt_adjust+=item['wt_adjust']
                sum_qty_book += item['qty_first'] + qty_in - qty_out
                sum_wt_book += item['wt_first'] + wt_in -wt_out
                
            if len(result)>=1:
                arr.append({
                                'default_code': 'Sub Total',
                                'name': '',
                                'quality': '-',
                                'quality_description': '-',
                                'qty_in': sum_qty_in,
                                'wt_in': sum_wt_in,
                                'qty_first': sum_qty_first,
                                'wt_first': sum_wt_first,
                                'qty_out': sum_qty_out,
                                'wt_out': sum_wt_out,
                                'qty_lost': sum_qty_lost,
                                'wt_lost': sum_wt_lost,
                                'qty_ship': sum_qty_ship,
                                'wt_ship': sum_wt_ship,
                                'qty_adjust': sum_qty_adjust,
                                'wt_adjust': sum_wt_adjust,
                                'qty_stock':  sum_qty_stock,
                                'wt_stock':  sum_wt_stock,
                                'qty_endbook': sum_qty_book,
                                'wt_endbook':sum_wt_book,
                                
                                })
   
            total_qty_first+= sum_qty_first
            total_qty_in += sum_qty_in
            total_qty_lost += sum_qty_lost
            total_qty_out += sum_qty_out
            total_qty_ship +=sum_qty_ship
            total_qty_stock += sum_qty_stock
            total_wt_first += sum_wt_first
            total_wt_in += sum_wt_in
            total_wt_lost += sum_wt_lost
            total_wt_stock += sum_wt_stock
            total_wt_ship += sum_wt_ship
            total_wt_out += sum_wt_out
            total_qty_endbook += sum_qty_book
            total_wt_endbook += sum_wt_book
            total_qty_adjust += sum_qty_adjust
            total_wt_adjust += sum_wt_adjust
  
        arr.append({
            'default_code': 'Total',
            'quality': '-',
            'quality_description': '-',
            'name': '',
            'qty_in': total_qty_in,
            'wt_in': total_wt_in,
            'qty_first': total_qty_first,
            'wt_first': total_wt_first,
            'qty_out': total_qty_out,
            'wt_out': total_wt_out,
            'qty_lost': total_qty_lost,
            'wt_lost': total_wt_lost,
            'qty_ship': total_qty_ship,
            'wt_ship': total_wt_ship,
            'qty_adjust': total_qty_adjust,
            'wt_adjust': total_wt_adjust,
            'qty_stock':  total_qty_stock,
            'wt_stock':  total_wt_stock,
            'qty_endbook': total_qty_endbook,
            'wt_endbook':total_wt_endbook,
                        })  
        # hpusa 13-07-2015               
            
        print 'End get information'    
        return arr
    

wizard_hpusa_material_request_report()

#===============================================================================
openoffice_report.openoffice_report(
     'report.report_rawmaterial_stock',
     'wizard.hpusa.warehouse.report',
     parser=wizard_hpusa_material_request_report
 )

openoffice_report.openoffice_report(
     'report.report_rawmaterial_stock_month',
     'wizard.hpusa.warehouse.report',
     parser=wizard_hpusa_material_request_report
 )  
 
openoffice_report.openoffice_report(
     'report.report_diamond_stock_sumary',
     'wizard.hpusa.warehouse.report',
     parser=wizard_hpusa_material_request_report
 )

openoffice_report.openoffice_report(
     'report.report_diamond_stock_sumary_month',
     'wizard.hpusa.warehouse.report',
     parser=wizard_hpusa_material_request_report
 )

openoffice_report.openoffice_report(
     'report.hpusa_inventory_report_sumary',
     'wizard.hpusa.warehouse.report',
     parser=wizard_hpusa_material_request_report
 )    
#===============================================================================

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
