
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

class wizard_hpusa_manufacturing_loss_report(osv.osv):
    _name = "wizard.hpusa.manufacturing.loss.report"

    _columns = {
            'report_type': fields.selection([('workerdetail','Loss of Goldsmith'),('mo','Loss of MO'),('sumary','Goldsmith Sumary')],'Report Type'),
            'date_from': fields.date('Date From', required=True),
            'date_to': fields.date('Date To',required=True),
            'worker': fields.many2one('hr.employee','Goldsmith'),
            'mo_ids': fields.many2many('mrp.production','sale_loss_report_id','manufacturing_loss_id','loss_id','Manufacturing Order'),
            'context':fields.html('Content'),
            'state':fields.selection([('get', 'get'),('choose','choose')]),

    }
    _defaults = {
        'state':'choose',
        'report_type': 'workerdetail',
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }   

    def view_report(self,cr, uid, ids, context=None):
        this = self.browse(cr, uid,ids,context =None)[0]
        html = ''
        if this.report_type =='mo':
            arr=[]
            arr= self.export_manufacturing_loss_sumary(cr, uid, this.date_from, this.date_to)
            if arr:
                html=self.create_html_view_mo_loss(cr, uid, this.date_from, this.date_to, arr)
                self.write(cr, uid,ids, {'state': 'get',
                                    'context':html }, context=context)

        elif this.report_type =='workerdetail':
            arr=[]
            arr= self.export_manufacturing_loss_detail(cr, uid, this.date_from, this.date_to, this.worker.id)
            if arr:
                html=self.create_html_view_goldsmith_detail(cr, uid, this.date_from, this.date_to, this.worker.name, arr)
                self.write(cr, uid,ids, {'state': 'get',
                                    'context':html }, context=context)
        else:
            arr=[]
            arr= self.export_manufacturing_worker_sumary(cr, uid, this.date_from, this.date_to)
            if arr:
                html=self.create_html_view_goldsmith_summary(cr, uid, this.date_from, this.date_to, arr)
                self.write(cr, uid,ids, {'state': 'get',
                                    'context':html }, context=context)

        return  {
             'type': 'ir.actions.act_window',
             'res_model': 'wizard.hpusa.manufacturing.loss.report',
             'view_mode': 'form',
             'view_type': 'form',
             'res_id':this.id,
             'views': [(False, 'form')],
             'target': 'new',
                }

    def create_html_view_mo_loss(self,cr,uid, date_from,date_to,data):
        html=''
        if data:
            html +='<span contenteditable="false">'\
                        '<h1  style = "text-align:center"> BÁO CÁO CHI TIẾT SẢN XUẤT VÀ HAO HỤT CÁC SẢN PHẨM  </h1>'\
                        '<h4 style = "text-align:center"> Từ ngày: '+str(date_from)+ ' Đến ngày:' + str(date_to)+' </h4>'\
                        '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                        '<thead class = "theads">'\
                        '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">STT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">MÃ SẢN XUẤT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >STYLE NUMBER</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >LOẠI VÀNG</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >ĐƠN HÀNG</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG GIAO(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG TRẢ VỀ(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG SỬ DỤNG(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >THÀNH PHẨM</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG TRONG TP</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL HỘT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL HAO</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >% HAO </th>'\
                        '</tr>'\
                        '</thead>'\
                        '<tbody>'
            for i in data:
                        html += '<tr class = "trs">'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['sequence'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['mrp_name'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['product_name'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['style_number'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['sale_order'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_delivery'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_return'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_used'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['finished_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['net_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['loss_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['loss_percent'])+'</td>'\
                                '</tr>'
            html += '</tbody>'\
                            '</table>'\
                            '</span>'
        else :
            html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BÁO CÁO CHI TIẾT SẢN XUẤT VÀ HAO HỤT CÁC SẢN PHẨM  </h1>'\
                        '<h4 style = "text-align:center"> Từ Ngày: '+str(date_from)+ ' Đến ngày:' + str(date_to)+' </h4>'\
                        '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                        '<thead class = "theads">'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['sequence'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['mrp_name'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['product_name'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['style_number'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['sale_order'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['metal_delivery'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['metal_return'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['metal_used'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['finished_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['net_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['diamond_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['loss_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center">'+ str(i['loss_percent'])+'</td>'\
                    '</tr>'\
                    '</thead>'\
                    '<tbody>'\
                    '</tbody>'\
                    '</table>'\
                    '</span>'
        return html

    def create_html_view_goldsmith_detail(self,cr,uid, date_from,date_to,gold_smith,data):
        html=''
        if data:
            html +='<span contenteditable="false">'\
                        '<h1  style = "text-align:center"> BÁO CÁO CHI TIẾT HAO HỤT THỢ  </h1>'\
                        '<h4 style = "text-align:center"> Từ ngày: '+str(date_from)+ ' Đến ngày:' + str(date_to)+' </h4>'\
                        '<h4 style = "text-align:center"> Tên thợ: '+str(gold_smith)+' </h4>'\
                        '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                        '<thead class = "theads">'\
                        '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">STT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">MÃ SẢN XUẤT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >CÔNG ĐOẠN</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >NGÀY LÀM</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG GIAO</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG GIAO(24K)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ VÀNG</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ VÀNG(24K)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >HỘT GIAO (Ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ HỘT(ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TP, BTP GIAO</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ TP, BTP(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL HAO </th>'\
                        '</tr>'\
                        '</thead>'\
                        '<tbody>'
            for i in data:
                        html += '<tr class = "trs">'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['sequence'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['mrp_name'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['line_name'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['actual_date'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_delivery'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_24k_delivery'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_return'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_24k_return'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_delivery_ct'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_return_ct'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['finish_delivery'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['finish_return'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['loss'])+'</td>'\
                                '</tr>'
            html += '</tbody>'\
                            '</table>'\
                            '</span>'
        else :
            html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BÁO CÁO CHI TIẾT HAO HỤT THỢ  </h1>'\
                        '<h4 style = "text-align:center"> Từ ngày: '+str(date_from)+ ' Đến ngày:' + str(date_to)+' </h4>'\
                        '<h4 style = "text-align:center"> Tên thợ: '+str(gold_smith)+' </h4>'\
                        '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                        '<thead class = "theads">'\
                        '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">STT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">MÃ SẢN XUẤT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >CÔNG ĐOẠN</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >NGÀY LÀM</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG GIAO</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >VÀNG GIAO(24K)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ VÀNG</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ VÀNG(24K)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >HỘT GIAO (Ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ HỘT(ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TP, BTP GIAO</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TRẢ TP, BTP(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL HAO </th>'\
                    '</tr>'\
                    '</thead>'\
                    '<tbody>'\
                    '</tbody>'\
                    '</table>'\
                    '</span>'
        return html

    def create_html_view_goldsmith_summary(self,cr,uid, date_from,date_to,data):
        html=''
        if data:
            html +='<span contenteditable="false">'\
                        '<h1  style = "text-align:center"> BÁO CÁO TỔNG HỢP HAO HỤT THỢ </h1>'\
                        '<h4 style = "text-align:center"> Từ ngày: '+str(date_from)+ ' Đến ngày:' + str(date_to)+' </h4>'\
                        '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                        '<thead class = "theads">'\
                        '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">STT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">Tên Thợ</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Vàng Giao(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Giao xoàn(ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Giao xoàn(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Xoàn trả lại(ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Xoàn trả lại(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >SL Xoàn mất</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL Xoàn mất</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL Thành phẩm</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL Hao hụt(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >% Hao hụt</th>'\
                        '</tr>'\
                        '</thead>'\
                        '<tbody>'
            for i in data:
                        html += '<tr class = "trs">'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['sequence'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i['employee_name'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['metal_delivery'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_delivery_ct'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_delivery_gr'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_return_ct'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_return_gr'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_loss_qty'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['diamond_loss_ct'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['finish_return'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['loss_weight'])+'</td>'\
                                '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i['loss_percent'])+'</td>'\
                                '</tr>'
            html += '</tbody>'\
                            '</table>'\
                            '</span>'
        else :
            html +='<span contenteditable="false">'\
                '<h1  style = "text-align:center"> BÁO CÁO TỔNG HỢP HAO HỤT THỢ </h1>'\
                        '<h4 style = "text-align:center"> Từ ngày: '+str(date_from)+ ' Đến ngày:' + str(date_to)+' </h4>'\
                        '<table  width="1000px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                        '<thead class = "theads">'\
                        '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">STT</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">Tên Thợ</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Vàng Giao(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Giao xoàn(ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Giao xoàn(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Xoàn trả lại(ct)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >Xoàn trả lại(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >SL Xoàn mất</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL Xoàn mất</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL Thành phẩm</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >TL Hao hụt(gr)</th>'\
                        '<th class = "ths"  style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >% Hao hụt</th>'\
                    '</tr>'\
                    '</thead>'\
                    '<tbody>'\
                    '</tbody>'\
                    '</table>'\
                    '</span>'
        return html

    def action_export(self, cr, uid, ids, context=None):

        #======================= Export Data to EXCEL ============================================
        this = self.browse(cr, uid,ids,context =None)[0]
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['report_type','date_from','date_to','worker','mo_ids'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['worker']= this.worker.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hpusa.manufacturing.loss.report'

        if res['report_type'] =='mo':
            datas['line1']  = self.export_manufacturing_loss_sumary(cr,uid,res['date_from'],res['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'manufacturing_loss_report_sumary',
                'datas'         : datas,}
        elif res['report_type'] =='workerdetail':
            datas['line1']  = self.export_manufacturing_loss_detail(cr, uid,res['date_from'],res['date_to'],this.worker.id)
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'manufacturing_loss_report_worker',
                'datas'         : datas,}
        else:
            datas['line1']  = self.export_manufacturing_worker_sumary(cr, uid,res['date_from'],res['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'manufacturing_loss_worker_report_sumary',
                'datas'         : datas,}

        return True

    def export_manufacturing_loss_sumary(self,cr,uid,date_from,date_to):

        mt = datetime.strptime(date_to,'%Y-%m-%d')
        date_to = str(mt+relativedelta.relativedelta( days=1))[:10]

        sql = '''
            SELECT mrp.id,
            mrp.name as mrp_name,
            pp.name_template as product_name,
            pp.default_code  as style_number,
            pp.metal_type as metal_type,
            so.name as sale_order,
            mrp.metal_delivery as metal_delivery,
            mrp.metal_return as metal_return,
            mrp.metal_used as metal_used,
            mrp.finished_weight as finished_weight,
            mrp.metal_in_product as net_weight,
            mrp.diamond_weight as diamond_weight,
            mrp.loss_weight as loss_weight,
            mrp.loss_percent as loss_percent,
            mrp.loss_weight_24k as loss_weight_24k
            FROM mrp_production mrp,
            product_product pp,
            sale_order so
            WHERE pp.id = mrp.product_id
            AND so.id= mrp.so_id
            AND mo_date >= to_date('%s','yyyy-mm-dd')
            AND mo_date < to_date('%s','yyyy-mm-dd')
            AND pp.metal_class ='gold'

            '''%(date_from,date_to)
        cr.execute(sql)
        print sql
        result = cr.dictfetchall()

        arr = []

        sum_metal_delivery = 0
        sum_metal_return =0
        sum_meta_used =0
        sum_finished_weight =0
        sum_net_weight = 0
        sum_diamond_weight =0
        sum_loss_weight =0
        sum_loss_24k =0

        arr.append({
                            'sequence': 'Gold',
                            'mrp_name': '-',
                            'product_name': '-',
                            'style_number': '-',
                            'metal_type': '-',
                            'sale_order': '-',
                            'metal_delivery':'-',
                            'metal_return': '-',
                            'metal_used': '-',
                            'finished_weight': '-',
                            'net_weight': '-',
                            'diamond_weight': '-',
                            'loss_weight': '-',
                            'loss_percent': '-',
                            'loss_24k':'-',
                            })
        sequence =0

        for item in result:

            arr.append({
                            'sequence': sequence,
                            'mrp_name': item['mrp_name'],
                            'product_name': item['product_name'],
                            'style_number': item['style_number'],
                            'metal_type': item['metal_type'],
                            'sale_order': item['sale_order'],
                            'metal_delivery': item['metal_delivery'],
                            'metal_return': item['metal_return'],
                            'metal_used': item['metal_used'],
                            'finished_weight': item['finished_weight'],
                            'net_weight': item['net_weight'],
                            'diamond_weight': item['diamond_weight'],
                            'loss_weight': item['loss_weight'],
                            'loss_percent': round( float(item['loss_percent'] or 0.0),2),
                            'loss_24k': round(float(item['loss_weight_24k'] or 0.0),2),
                            })

            sum_metal_delivery += round(float(item['metal_delivery'] or 0.0),2)
            sum_metal_return +=round(float(item['metal_return'] or 0.0),2)
            sum_meta_used +=round(float(item['metal_used'] or 0.0),2)
            sum_finished_weight +=round(float(item['finished_weight'] or 0.0),2)
            sum_net_weight += round(float(item['net_weight'] or 0.0),2)
            sum_diamond_weight +=round(float(item['diamond_weight'] or 0.0),2)
            sum_loss_weight +=round(float(item['loss_weight'] or 0.0),2)
            sum_loss_24k +=round(float(item['loss_weight_24k'] or 0.0),2)
            sequence +=1

        arr.append({
                            'sequence': '--',
                            'mrp_name': 'Total',
                            'product_name': '-',
                            'style_number': '-',
                            'metal_type': '-',
                            'sale_order': '-',
                            'metal_delivery': sum_metal_delivery,
                            'metal_return': sum_metal_return,
                            'metal_used': sum_meta_used,
                            'finished_weight': sum_finished_weight,
                            'net_weight': sum_net_weight,
                            'diamond_weight': sum_diamond_weight,
                            'loss_weight': sum_loss_weight,
                            'loss_percent':'-',
                            'loss_24k':sum_loss_24k,
                            })

        #========================================== PLATINUM ====================================

        sql_platinum = '''
            SELECT mrp.id,
            mrp.name as mrp_name,
            pp.name_template as product_name,
            pp.default_code  as style_number,
            pp.metal_type as metal_type,
            so.name as sale_order,
            mrp.metal_delivery as metal_delivery,
            mrp.metal_return as metal_return,
            mrp.metal_used as metal_used,
            mrp.finished_weight as finished_weight,
            mrp.metal_in_product as net_weight,
            mrp.diamond_weight as diamond_weight,
            mrp.loss_weight as loss_weight,
            mrp.loss_percent as loss_percent
            FROM mrp_production mrp,
            product_product pp,
            sale_order so
            WHERE pp.id = mrp.product_id
            AND so.id= mrp.so_id
            AND mo_date >= to_date('%s','yyyy-mm-dd')
            AND mo_date < to_date('%s','yyyy-mm-dd')
            AND pp.metal_class ='platinum'

            '''%(date_from,date_to)

        cr.execute(sql_platinum)
        print sql
        result_platinum = cr.dictfetchall()

        sequence =0

        arr.append({
                            'sequence': 'Platinum',
                            'mrp_name': '-',
                            'product_name': '-',
                            'style_number': '-',
                            'metal_type': '-',
                            'sale_order': '-',
                            'metal_delivery':'-',
                            'metal_return': '-',
                            'metal_used': '-',
                            'finished_weight': '-',
                            'net_weight': '-',
                            'diamond_weight': '-',
                            'loss_weight': '-',
                            'loss_percent': '-',
                            'loss_24k':'-',
                            })
        sum_metal_delivery = 0
        sum_metal_return =0
        sum_meta_used =0
        sum_finished_weight =0
        sum_net_weight = 0
        sum_diamond_weight =0
        sum_loss_weight =0
        sum_loss_24k =0
        for item in result_platinum:

            arr.append({
                            'sequence': sequence,
                            'mrp_name': item['mrp_name'],
                            'product_name': item['product_name'],
                            'style_number': item['style_number'],
                            'metal_type': item['metal_type'],
                            'sale_order': item['sale_order'],
                            'metal_delivery': item['metal_delivery'],
                            'metal_return': item['metal_return'],
                            'metal_used': item['metal_used'],
                            'finished_weight': item['finished_weight'],
                            'net_weight': item['net_weight'],
                            'diamond_weight': item['diamond_weight'],
                            'loss_weight': item['loss_weight'],
                            'loss_percent': round(float(item['loss_percent']),2),
                            'loss_24k':'-',
                            })
            sequence +=1

            sum_metal_delivery += round(float(item['metal_delivery']or 0.0),2)
            sum_metal_return +=round(float(item['metal_return'] or 0.0),2)
            sum_meta_used +=round(float(item['metal_used'] or 0.0),2)
            sum_finished_weight +=round(float(item['finished_weight'] or 0.0),2)
            sum_net_weight += round(float(item['net_weight'] or 0.0),2)
            sum_diamond_weight +=round(float(item['diamond_weight'] or 0.0),2)
            sum_loss_weight +=round(float(item['loss_weight'] or 0.0),2)
            sum_loss_24k =0
            sequence +=1

        arr.append({
                            'sequence': '--',
                            'mrp_name': 'Total',
                            'product_name': '-',
                            'style_number': '-',
                            'metal_type': '-',
                            'sale_order': '-',
                            'metal_delivery': sum_metal_delivery,
                            'metal_return': sum_metal_return,
                            'metal_used': sum_meta_used,
                            'finished_weight': sum_finished_weight,
                            'net_weight': sum_net_weight,
                            'diamond_weight': sum_diamond_weight,
                            'loss_weight': sum_loss_weight,
                            'loss_percent':'-',
                            'loss_24k':sum_loss_24k,
                            })


        return arr

    def export_manufacturing_worker_sumary(self,cr,uid,date_from,date_to):
        mt = datetime.strptime(date_to,'%Y-%m-%d')
        date_to = str(mt+relativedelta.relativedelta( days=1))[:10]
        arr = []
        sql_get_employee ='''
        select distinct mpwl.employee_id as employee_id,
           he.name_related as employee_name
           from mrp_production_workcenter_line mpwl,
           mrp_production mp,
           hr_employee he
           where mp.id = mpwl.production_id
           AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
           AND mp.mo_date < to_date('%s','YYYY-MM-DD')
           AND he.id = mpwl.employee_id
           AND mpwl.employee_id  IS NOT NULL
        ''' %(date_from,date_to)
        cr.execute(sql_get_employee)
        print sql_get_employee
        employee_ids = cr.dictfetchall()

        arr.append({
                      'sequence':'Gold (Hao hụt vàng)',
                                'employee_name': '-',
                                'metal_delivery':'-',
                                'metal_24k_delivery': '-',
                                'metal_return': '-',
                                'metal_24k_return': '-',
                                'diamond_delivery_ct': '-',
                                'diamond_delivery_gr': '-',
                                'diamond_return_ct': '-',
                                'diamond_return_gr': '-',
                                'finish_delivery': '-',
                                'finish_return': '-',
                                'loss_weight': '-',
                                'loss': '-',
                                'loss_limit':'',
                                'loss_over':'',
                                'loss_24k':'',
                                'loss_limit_24k':'',
                                'loss_over_24k':'',
                                'net_weight':'-',
                                'percent':'-',

                                    })

   
        
        if employee_ids:
            sequence = 1
            for employee in employee_ids:
                employee_id= employee['employee_id']
                sql = '''
                    SELECT
            mp.name,
            mpwl.date_planned actual_date,
            mpwl.name line_name,
            round(coalesce(sum(tab1.qty),0),3) as metal_delivery,
            coalesce(sum(tab1.qty_24k),0) as metal_24k_delivery,
            round(coalesce(sum(tab2.qty),0),3) as metal_return,
            coalesce(sum(tab2.qty_24k),0) as metal_24k_return,
            round(coalesce(sum(tab3.weight_ct),0),3) as diamond_delivery_ct,
            round(coalesce(sum(tab3.weight_gr),0),3) as diamond_delivery_gr,
            round(coalesce(sum(tab4.weight_ct),0),3) as diamond_return_ct,
            round(coalesce(sum(tab4.weight_gr),0),3) as diamond_return_gr,
            round(coalesce(sum(tab5.weight_gr),0),3) as finish_delivery,
            round(coalesce(sum(tab6.weight_gr),0),3) as finish_return,
            round(coalesce(sum(diamond.weight_gr),0),3) as diamond_weight,
              round(coalesce(sum(tab1.qty),0),3) -  round(coalesce(sum(tab2.qty),0),3)  +(round(coalesce(sum(tab5.weight_gr),0),3)
            -round(coalesce(sum(tab5.weight_gr)/sum(tab5.weight_gr)*sum(diamond.weight_gr),0),3)) -
            ((round(coalesce(sum(tab6.weight_gr),0),3)
            -round(coalesce(sum(tab6.weight_gr)/sum(tab6.weight_gr)*sum(diamond.weight_gr),0),3))) as loss_weight,
            pp.coeff_24k as coeff_24k,
           wk.percent as percent,
            mp.metal_in_product as net_weight,
            round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
            as loss,
            mp.metal_in_product * wk.percent /100
            as loss_limit,
            round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
             -  ( mp.metal_in_product * wk.percent /100)
             as loss_over,
           ( round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3))))
            * coeff_24k as loss_24k,
               ( mp.metal_in_product* wk.percent /100)
            *coeff_24k as loss_limit_24k,
             (round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
             -  ( mp.metal_in_product* wk.percent /100))
            *coeff_24k as loss_over_24k
            from mrp_production_workcenter_line mpwl
             left join mrp_workcenter as wk on(wk.id = mpwl.workcenter_id)
            left join mrp_production as mp on(mp.id = mpwl.production_id)
            left join product_product as pp on (pp.id = mp.product_id)
            left join
            --- JOIN METAL DELIVERY  ---
                (SELECT mpwl.id as mpwl_id,    
                mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_delivery_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                AND sp.receiver =%s -- Employee
                                AND sp.wo_delivery_id IN (
                                 SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 --AND employee_id=1
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id,mpwl.name) as tab1 ON(tab1.mpwl_id = mpwl.id)
                left join ------------------- JOIN METAL RETURN -----------------------
                (SELECT mp.id mrp_id , mp.name mrp_name,mpwl.id as mpwl_id,mpwl.name mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_return_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                AND sp.shipper =%s -- Employee
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 --AND employee_id=1
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id, mp.name ,mpwl.id,mpwl.name)
                as tab2 ON(tab2.mpwl_id = mpwl.id)

                LEFT JOIN
--- DIAMOND DELIVERY  ---
                (SELECT mp.id mp_id,mp.name mp_name,mpwl.id mpwl_id, mpwl.name mpwl_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_delivery_id
                                AND sp.receiver = %s
                                AND sp.wo_delivery_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name,mpwl.id, mpwl.name)
                as tab3 ON(tab3.mpwl_id = mpwl.id)

                LEFT JOIN(
                -- DIAMOND RETURN ---
                SELECT mpwl.id as mpwl_id, mpwl.name mpwl_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_return_id
                                AND sp.shipper = %s
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name
                ) as tab4 ON(tab4.mpwl_id = mpwl.id)
                --- FINISH DELIVERY ---
                LEFT JOIN
                (SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_delivery_id
                                AND sp.receiver = %s
                                AND sp.wo_delivery_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name)
                as tab5 ON(tab5.mpwl_id = mpwl.id)
                --- FINISH RETURN ---
                left join (
                SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_return_id
                                AND sp.shipper = %s
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'   
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name
                ) as tab6 ON(tab6.mpwl_id = mpwl.id)
                left join
                --- DIAMOND IN FINISH PRODUCT ---
                (select mrp.id as id, coalesce(sum (weight_ct),0) as weight_ct, coalesce(sum(weight_gr),0) as weight_gr
                from(
                SELECT mp.id as id ,mp.name  as name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_delivery_id = mpwl.id
                                AND sp.wo_delivery_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name
                UNION ALL
                -- TINH TRONG LUONG DIAMOND TRA VE
                SELECT mp.id as id,mp.name as name,
                                coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_return_id = mpwl.id
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name
                UNION ALL
                -- TINH TRONG LUONG DIAMOND BE, MAT
                SELECT mp.id as id,mp.name as name,
                                coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_lost_id = mpwl.id
                                AND sp.shipper = %s
                                AND sp.wo_lost_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id, mp.name
                ) as mrp
                GROUP BY mrp.id
                ) as diamond ON(diamond.id = mpwl.production_id)
                group by mp.name,mpwl.date_planned, mpwl.name,pp.coeff_24k,wk.percent, mp.metal_in_product
                having coalesce(sum(tab1.qty),0)
                +coalesce(sum(tab1.qty_24k),0)+ coalesce(sum(tab2.qty),0)
                +coalesce(sum(tab2.qty_24k),0)+ coalesce(sum(tab3.weight_ct),0)
                +coalesce(sum(tab3.weight_gr),0)+ coalesce(sum(tab4.weight_ct),0)
                +coalesce(sum(tab4.weight_gr),0)+ coalesce(sum(tab5.weight_gr),0)
                +coalesce(sum(tab6.weight_gr),0)<>0
                order by mp.name,mpwl.name ;

            ''' %(date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to)

                cr.execute(sql)
                print sql
                result = cr.dictfetchall()
                sum_metal_delivery = 0
                sum_metal_24k_delivery= 0
                sum_metal_return =0
                sum_metal_24k_return =0
                sum_diamond_delivery_ct = 0
                sum_diamond_delivery_gr =0
                sum_diamond_return_ct =0
                sum_diamond_return_gr =0
                sum_finish_delivery=0
                sum_finish_return=0
                sum_loss_weight =0
                sum_loss =0
                sum_loss_limit = 0
                sum_loss_over = 0
                sum_loss_24k = 0
                sum_loss_limit_24k = 0
                sum_loss_over_24k = 0
                for item in result:
                    sum_metal_delivery +=item['metal_delivery']
                    sum_metal_24k_delivery+=item['metal_24k_delivery']
                    sum_metal_return +=item['metal_return']
                    sum_metal_24k_return +=item['metal_24k_return']
                    sum_diamond_delivery_ct +=item['diamond_delivery_ct']
                    sum_diamond_delivery_gr += item['diamond_delivery_gr']
                    sum_diamond_return_ct +=item['diamond_return_gr']
                    sum_diamond_return_gr +=item['metal_delivery']
                    sum_finish_delivery+=item['finish_delivery']
                    sum_finish_return +=item['finish_return']
                    sum_loss_weight+= round(float(item['loss_weight'] or 0.0),3)
                    sum_loss +=round(float(item['loss'] or 0.0),3)
                    sum_loss_limit += round(float(item['loss_limit'] or 0.0),3)
                    sum_loss_over += round(float(item['loss_over'] or 0.0),3)
                    sum_loss_24k += round(float(item['loss_24k'] or 0.0),3)
                    sum_loss_limit_24k += round(float(item['loss_limit_24k'] or 0.0),3)
                    sum_loss_over_24k += round(float(item['loss_over_24k'] or 0.0),3)
                sequence += 1
                arr.append({
                                'sequence':sequence,
                                'employee_name': employee['employee_name'],
                                'metal_delivery': sum_metal_delivery,
                                'metal_24k_delivery':sum_metal_24k_delivery,
                                'metal_return': sum_metal_return,
                                'metal_24k_return': sum_metal_24k_return,
                                'diamond_delivery_ct': sum_diamond_delivery_ct,
                                'diamond_delivery_gr': sum_diamond_delivery_gr,
                                'diamond_return_ct': sum_diamond_return_ct,
                                'diamond_return_gr': sum_diamond_return_gr,
                                'finish_delivery': sum_finish_delivery,
                                'finish_return': sum_finish_return,
                                'loss_weight': sum_loss_weight,
                                'loss': sum_loss,
                                'loss_limit':sum_loss_limit,
                                'loss_over':sum_loss_over,
                                'loss_24k':sum_loss_24k,
                                'loss_limit_24k':sum_loss_limit_24k,
                                'loss_over_24k':sum_loss_over_24k,
                                'net_weight':'-',
                                'percent':'-',
                                })
    #============================================= PLATINUM =====================================

        if employee_ids:
            sequence = 1
            for employee in employee_ids:
                employee_id= employee['employee_id']
                sql_platinum = '''
        
                SELECT
                    mp.name,
                    mpwl.date_planned actual_date,
                    mpwl.name line_name,
                    round(coalesce(sum(tab1.qty),0),3) as metal_delivery,
                    coalesce(sum(tab1.qty_24k),0) as metal_24k_delivery,
                    round(coalesce(sum(tab2.qty),0),3) as metal_return,
                    coalesce(sum(tab2.qty_24k),0) as metal_24k_return,
                    round(coalesce(sum(tab3.weight_ct),0),3) as diamond_delivery_ct,
                    round(coalesce(sum(tab3.weight_gr),0),3) as diamond_delivery_gr,
                    round(coalesce(sum(tab4.weight_ct),0),3) as diamond_return_ct,
                    round(coalesce(sum(tab4.weight_gr),0),3) as diamond_return_gr,
                    round(coalesce(sum(tab5.weight_gr),0),3) as finish_delivery,
                    round(coalesce(sum(tab6.weight_gr),0),3) as finish_return,
                    round(coalesce(sum(diamond.weight_gr),0),3) as diamond_weight,
                      round(coalesce(sum(tab1.qty),0),3) -  round(coalesce(sum(tab2.qty),0),3)  +(round(coalesce(sum(tab5.weight_gr),0),3)
                    -round(coalesce(sum(tab5.weight_gr)/sum(tab5.weight_gr)*sum(diamond.weight_gr),0),3)) -
                    ((round(coalesce(sum(tab6.weight_gr),0),3)
                    -round(coalesce(sum(tab6.weight_gr)/sum(tab6.weight_gr)*sum(diamond.weight_gr),0),3))) as loss_weight,
                    pp.coeff_24k as coeff_24k,
                   wk.percent as percent,
                    mp.metal_in_product as net_weight,
                    round(coalesce(sum(tab1.qty),0),3)
                    + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
                    - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
                    as loss,
                    mp.metal_in_product * wk.percent /100
                    as loss_limit,
                    round(coalesce(sum(tab1.qty),0),3)
                    + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
                    - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
                     -  ( mp.metal_in_product * wk.percent /100)
                     as loss_over,
                   ( round(coalesce(sum(tab1.qty),0),3)
                    + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
                    - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3))))
                    * coeff_24k as loss_24k,
                       ( mp.metal_in_product* wk.percent /100)
                    *coeff_24k as loss_limit_24k,
                     (round(coalesce(sum(tab1.qty),0),3)
                    + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
                    - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
                     -  ( mp.metal_in_product* wk.percent /100))
                    *coeff_24k as loss_over_24k
                    from mrp_production_workcenter_line mpwl
                     left join mrp_workcenter as wk on(wk.id = mpwl.workcenter_id)
                    left join mrp_production as mp on(mp.id = mpwl.production_id)
                    left join product_product as pp on (pp.id = mp.product_id)
                    left join
                    --- JOIN METAL DELIVERY  ---
                        (SELECT mpwl.id as mpwl_id,    
                        mpwl.name as mpwl_name,
                                        coalesce (SUM(sm.product_qty),0) as qty ,
                                        coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                        FROM stock_move sm,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production_workcenter_line mpwl,
                                        mrp_production mp
                                        WHERE sp.hp_transfer_type='delivery'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='metal'
                                        AND pp.metal_class = 'platinum'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND sp.wo_delivery_id = mpwl.id
                                        AND mpwl.production_id = mp.id
                                        AND sp.receiver =%s -- Employee
                                        AND sp.wo_delivery_id IN (
                                         SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                        
                                         --AND employee_id=1
                                         )
                                        AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mpwl.id,mpwl.name) as tab1 ON(tab1.mpwl_id = mpwl.id)
                        left join ------------------- JOIN METAL RETURN -----------------------
                        (SELECT mp.id mrp_id , mp.name mrp_name,mpwl.id as mpwl_id,mpwl.name mpwl_name,
                                        coalesce (SUM(sm.product_qty),0) as qty ,
                                        coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                        FROM stock_move sm,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production_workcenter_line mpwl,
                                        mrp_production mp
                                        WHERE sp.hp_transfer_type='return'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='metal'
                                        AND pp.metal_class = 'platinum'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND sp.wo_return_id = mpwl.id
                                        AND mpwl.production_id = mp.id
                                        AND sp.shipper =%s -- Employee
                                        AND sp.wo_return_id IN (
                                          SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                         --AND employee_id=1
                                         )
                                        AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mp.id, mp.name ,mpwl.id,mpwl.name)
                        as tab2 ON(tab2.mpwl_id = mpwl.id)
        
                        LEFT JOIN
        --- DIAMOND DELIVERY  ---
                        (SELECT mp.id mp_id,mp.name mp_name,mpwl.id mpwl_id, mpwl.name mpwl_name,
                                        coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                        coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                        FROM stock_move sm ,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production mp,
                                        mrp_production_workcenter_line mpwl
                                        WHERE sp.hp_transfer_type='delivery'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='diamonds'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND mp.id = mpwl.production_id
                                        AND mpwl.id = sp.wo_delivery_id
                                        AND sp.receiver = %s
                                        AND sp.wo_delivery_id IN (
                                        SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                         )
                                        AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mp.id,mp.name,mpwl.id, mpwl.name)
                        as tab3 ON(tab3.mpwl_id = mpwl.id)
        
                        LEFT JOIN(
                        -- DIAMOND RETURN ---
                        SELECT mpwl.id as mpwl_id, mpwl.name mpwl_name,
                                        coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                        coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                        FROM stock_move sm ,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production mp,
                                        mrp_production_workcenter_line mpwl
                                        WHERE sp.hp_transfer_type='return'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='diamonds'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND mp.id = mpwl.production_id
                                        AND mpwl.id = sp.wo_return_id
                                        AND sp.shipper = %s
                                        AND sp.wo_return_id IN (
                                          SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                         )
                                        AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mpwl.id, mpwl.name
                        ) as tab4 ON(tab4.mpwl_id = mpwl.id)
                        --- FINISH DELIVERY ---
                        LEFT JOIN
                        (SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                        coalesce (SUM(sm.product_qty),0) as qty ,
                                        coalesce(SUM(sm.weight_mo),0) as weight_gr
                                        FROM stock_move sm ,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production mp,
                                        mrp_production_workcenter_line mpwl
                                        WHERE sp.hp_transfer_type='delivery'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='finish_product'
                                        AND pp.metal_class = 'platinum'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND mp.id= mpwl.production_id
                                        AND mpwl.id= sp.wo_delivery_id
                                        AND sp.receiver = %s
                                        AND sp.wo_delivery_id IN (
                                          SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                         )
                                         AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mpwl.id, mpwl.name)
                        as tab5 ON(tab5.mpwl_id = mpwl.id)
                        --- FINISH RETURN ---
                        left join (
                        SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                        coalesce (SUM(sm.product_qty),0) as qty ,
                                        coalesce(SUM(sm.weight_mo),0) as weight_gr
                                        FROM stock_move sm ,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production mp,
                                        mrp_production_workcenter_line mpwl
                                        WHERE sp.hp_transfer_type='return'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='finish_product'
                                        AND pp.metal_class = 'platinum'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND mp.id= mpwl.production_id
                                        AND mpwl.id= sp.wo_return_id
                                        AND sp.shipper = %s
                                        AND sp.wo_return_id IN (
                                          SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'   
                                         )
                                         AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mpwl.id, mpwl.name
                        ) as tab6 ON(tab6.mpwl_id = mpwl.id)
                        left join
                        --- DIAMOND IN FINISH PRODUCT ---
                        (select mrp.id as id, coalesce(sum (weight_ct),0) as weight_ct, coalesce(sum(weight_gr),0) as weight_gr
                        from(
                        SELECT mp.id as id ,mp.name  as name,
                                        coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                        coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                        FROM stock_move sm ,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production mp,
                                        mrp_production_workcenter_line mpwl
                                        WHERE sp.hp_transfer_type='delivery'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='diamonds'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND mp.id = mpwl.production_id
                                        AND sp.wo_delivery_id = mpwl.id
                                        AND sp.wo_delivery_id IN (
                                          SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                         )
                                         AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mp.id,mp.name
                        UNION ALL
                        -- TINH TRONG LUONG DIAMOND TRA VE
                        SELECT mp.id as id,mp.name as name,
                                        coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                        coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                        FROM stock_move sm ,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production mp,
                                        mrp_production_workcenter_line mpwl
                                        WHERE sp.hp_transfer_type='return'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='diamonds'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND mp.id = mpwl.production_id
                                        AND sp.wo_return_id = mpwl.id
                                        AND sp.wo_return_id IN (
                                          SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                         )
                                        AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mp.id,mp.name
                        UNION ALL
                        -- TINH TRONG LUONG DIAMOND BE, MAT
                        SELECT mp.id as id,mp.name as name,
                                        coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                        coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                        FROM stock_move sm ,
                                        stock_picking sp,
                                        product_product pp,
                                        mrp_production mp,
                                        mrp_production_workcenter_line mpwl
                                        WHERE sp.hp_transfer_type='return'
                                        --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                        --AND sm.date < to_date('%s','YYYY-MM-DD')
                                        AND sm.state = 'done'
                                        AND pp.hp_type ='diamonds'
                                        AND sm.product_id =pp.id
                                        AND sm.picking_id= sp.id
                                        AND mp.id = mpwl.production_id
                                        AND sp.wo_lost_id = mpwl.id
                                        AND sp.shipper = %s
                                        AND sp.wo_lost_id IN (
                                        SELECT mpwl.id
                                         FROM mrp_production_workcenter_line mpwl,
                                         mrp_production mp,
                                         product_product pp
                                         WHERE mp.id = mpwl.production_id
                                         AND mp.product_id = pp.id
                                         AND pp.metal_class = 'platinum'
                                         )
                                        AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                        AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                        GROUP BY mp.id, mp.name
                        ) as mrp
                        GROUP BY mrp.id
                        ) as diamond ON(diamond.id = mpwl.production_id)
                        group by mp.name,mpwl.date_planned, mpwl.name,pp.coeff_24k,wk.percent, mp.metal_in_product
                        having coalesce(sum(tab1.qty),0)
                        +coalesce(sum(tab1.qty_24k),0)+ coalesce(sum(tab2.qty),0)
                        +coalesce(sum(tab2.qty_24k),0)+ coalesce(sum(tab3.weight_ct),0)
                        +coalesce(sum(tab3.weight_gr),0)+ coalesce(sum(tab4.weight_ct),0)
                        +coalesce(sum(tab4.weight_gr),0)+ coalesce(sum(tab5.weight_gr),0)
                        +coalesce(sum(tab6.weight_gr),0)<>0
                        order by mp.name,mpwl.name ;
        
                    ''' %(date_from,date_to,
                          employee_id,
                          date_from,date_to,
                          date_from,date_to,
                          employee_id,
                          date_from,date_to,
                          date_from,date_to,
                          employee_id,
                          date_from,date_to,
                          date_from,date_to,
                          employee_id,
                          date_from,date_to,
                          date_from,date_to,
                          employee_id,
                          date_from,date_to,
                          date_from,date_to,
                          employee_id,
                          date_from,date_to,
                          date_from,date_to,
                          date_from,date_to,
                          date_from,date_to,
                          date_from,date_to,
                          date_from,date_to,
                          employee_id,
                          date_from,date_to)
                cr.execute(sql_platinum)
                print sql_platinum
                result_platinum = cr.dictfetchall()
                sum_metal_delivery_pt = 0
                sum_metal_24k_delivery_pt= 0
                sum_metal_return_pt =0
                sum_metal_24k_return_pt =0
                sum_diamond_delivery_ct_pt = 0
                sum_diamond_delivery_gr_pt =0
                sum_diamond_return_ct_pt =0
                sum_diamond_return_gr_pt =0
                sum_finish_delivery_pt=0
                sum_finish_return_pt=0
                sum_loss_weight_pt =0
                sum_loss_pt =0
                sum_loss_limit_pt = 0
                sum_loss_over_pt = 0
                sum_loss_24k_pt = 0
                sum_loss_limit_24k_pt = 0
                sum_loss_over_24k_pt = 0
                arr.append({
                                  'sequence':'Platinum (Hao hụt platinum)',
                                            'employee_name': '-',
                                            'metal_delivery':'-',
                                            'metal_24k_delivery': '-',
                                            'metal_return': '-',
                                            'metal_24k_return': '-',
                                            'diamond_delivery_ct': '-',
                                            'diamond_delivery_gr': '-',
                                            'diamond_return_ct': '-',
                                            'diamond_return_gr': '-',
                                            'finish_delivery': '-',
                                            'finish_return': '-',
                                            'loss_weight': '-',
                                            'loss': '-',
                                            'loss_limit':'',
                                            'loss_over':'',
                                            'loss_24k':'',
                                            'loss_limit_24k':'',
                                            'loss_over_24k':'',
                                            'net_weight':'-',
                                            'percent':'-',
                                                })
                for item in result_platinum:
                        sum_metal_delivery_pt +=item['metal_delivery']
                        sum_metal_24k_delivery_pt+=item['metal_24k_delivery']
                        sum_metal_return_pt +=item['metal_return']
                        sum_metal_24k_return_pt +=item['metal_24k_return']
                        sum_diamond_delivery_ct_pt +=item['diamond_delivery_ct']
                        sum_diamond_delivery_gr_pt += item['diamond_delivery_gr']
                        sum_diamond_return_ct_pt +=item['diamond_return_gr']
                        sum_diamond_return_gr_pt +=item['metal_delivery']
                        sum_finish_delivery_pt+=item['finish_delivery']
                        sum_finish_return_pt +=item['finish_return']
                        sum_loss_weight_pt+= round(float(item['loss_weight'] or 0.0),3)
                        sum_loss_pt +=round(float(item['loss'] or 0.0),3)
                        sum_loss_limit_pt += round(float(item['loss_limit'] or 0.0),3)
                        sum_loss_over_pt += round(float(item['loss_over'] or 0.0),3)
                        sum_loss_24k_pt += round(float(item['loss_24k'] or 0.0),3)
                        sum_loss_limit_24k_pt += round(float(item['loss_limit_24k'] or 0.0),3)
                        sum_loss_over_24k_pt += round(float(item['loss_over_24k'] or 0.0),3)
                sequence += 1
                arr.append({
                                        'sequence':sequence,
                                        'employee_name': employee['employee_name'],
                                        'metal_delivery': sum_metal_delivery_pt,
                                        'metal_24k_delivery':sum_metal_24k_delivery_pt,
                                        'metal_return': sum_metal_return_pt,
                                        'metal_24k_return': sum_metal_24k_return_pt,
                                        'diamond_delivery_ct': sum_diamond_delivery_ct_pt,
                                        'diamond_delivery_gr': sum_diamond_delivery_gr_pt,
                                        'diamond_return_ct': sum_diamond_return_ct_pt,
                                        'diamond_return_gr': sum_diamond_return_gr_pt,
                                        'finish_delivery': sum_finish_delivery_pt,
                                        'finish_return': sum_finish_return_pt,
                                        'loss_weight': sum_loss_weight_pt,
                                        'loss': sum_loss_pt,
                                        'loss_limit':sum_loss_limit_pt,
                                        'loss_over':sum_loss_over_pt,
                                        'loss_24k':sum_loss_24k_pt,
                                        'loss_limit_24k':sum_loss_limit_24k_pt,
                                        'loss_over_24k':sum_loss_over_24k_pt,
                                        'net_weight':'-',
                                        'percent':'-',
                                        })


        return arr

    def export_manufacturing_loss_detail(self,cr,uid,date_from,date_to,employee_id):

        arr = []
        mt = datetime.strptime(date_to,'%Y-%m-%d')
        date_to = str(mt+relativedelta.relativedelta( days=1))[:10]

        sql = '''
            SELECT
            mp.name,
            mpwl.date_planned actual_date,
            mpwl.name line_name,
            round(coalesce(sum(tab1.qty),0),3) as metal_delivery,
            coalesce(sum(tab1.qty_24k),0) as metal_24k_delivery,
            round(coalesce(sum(tab2.qty),0),3) as metal_return,
            coalesce(sum(tab2.qty_24k),0) as metal_24k_return,
            round(coalesce(sum(tab3.weight_ct),0),3) as diamond_delivery_ct,
            round(coalesce(sum(tab3.weight_gr),0),3) as diamond_delivery_gr,
            round(coalesce(sum(tab4.weight_ct),0),3) as diamond_return_ct,
            round(coalesce(sum(tab4.weight_gr),0),3) as diamond_return_gr,
            round(coalesce(sum(tab5.weight_gr),0),3) as finish_delivery,
            round(coalesce(sum(tab6.weight_gr),0),3) as finish_return,
            round(coalesce(sum(diamond.weight_gr),0),3) as diamond_weight,
              round(coalesce(sum(tab1.qty),0),3) -  round(coalesce(sum(tab2.qty),0),3)  +(round(coalesce(sum(tab5.weight_gr),0),3)
            -round(coalesce(sum(tab5.weight_gr)/sum(tab5.weight_gr)*sum(diamond.weight_gr),0),3)) -
            ((round(coalesce(sum(tab6.weight_gr),0),3)
            -round(coalesce(sum(tab6.weight_gr)/sum(tab6.weight_gr)*sum(diamond.weight_gr),0),3))) as loss_weight,
            pp.coeff_24k as coeff_24k,
           wk.percent as percent,
            mp.metal_in_product as net_weight,
            round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
            as loss,
            mp.metal_in_product * wk.percent /100
            as loss_limit,
            round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
             -  ( mp.metal_in_product * wk.percent /100)
             as loss_over,
           ( round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3))))
            * coeff_24k as loss_24k,
               ( mp.metal_in_product* wk.percent /100)
            *coeff_24k as loss_limit_24k,
             (round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
             -  ( mp.metal_in_product* wk.percent /100))
            *coeff_24k as loss_over_24k
            from mrp_production_workcenter_line mpwl
             left join mrp_workcenter as wk on(wk.id = mpwl.workcenter_id)
            left join mrp_production as mp on(mp.id = mpwl.production_id)
            left join product_product as pp on (pp.id = mp.product_id)
            left join
            --- JOIN METAL DELIVERY  ---
                (SELECT mpwl.id as mpwl_id,    
                mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_delivery_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                AND sp.receiver =%s -- Employee
                                AND sp.wo_delivery_id IN (
                                 SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                
                                 --AND employee_id=1
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id,mpwl.name) as tab1 ON(tab1.mpwl_id = mpwl.id)
                left join ------------------- JOIN METAL RETURN -----------------------
                (SELECT mp.id mrp_id , mp.name mrp_name,mpwl.id as mpwl_id,mpwl.name mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_return_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                AND sp.shipper =%s -- Employee
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 --AND employee_id=1
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id, mp.name ,mpwl.id,mpwl.name)
                as tab2 ON(tab2.mpwl_id = mpwl.id)

                LEFT JOIN
--- DIAMOND DELIVERY  ---
                (SELECT mp.id mp_id,mp.name mp_name,mpwl.id mpwl_id, mpwl.name mpwl_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_delivery_id
                                AND sp.receiver = %s
                                AND sp.wo_delivery_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name,mpwl.id, mpwl.name)
                as tab3 ON(tab3.mpwl_id = mpwl.id)

                LEFT JOIN(
                -- DIAMOND RETURN ---
                SELECT mpwl.id as mpwl_id, mpwl.name mpwl_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_return_id
                                AND sp.shipper = %s
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name
                ) as tab4 ON(tab4.mpwl_id = mpwl.id)
                --- FINISH DELIVERY ---
                LEFT JOIN
                (SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_delivery_id
                                AND sp.receiver = %s
                                AND sp.wo_delivery_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name)
                as tab5 ON(tab5.mpwl_id = mpwl.id)
                --- FINISH RETURN ---
                left join (
                SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_return_id
                                AND sp.shipper = %s
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'   
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name
                ) as tab6 ON(tab6.mpwl_id = mpwl.id)
                left join
                --- DIAMOND IN FINISH PRODUCT ---
                (select mrp.id as id, coalesce(sum (weight_ct),0) as weight_ct, coalesce(sum(weight_gr),0) as weight_gr
                from(
                SELECT mp.id as id ,mp.name  as name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_delivery_id = mpwl.id
                                AND sp.wo_delivery_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name
                UNION ALL
                -- TINH TRONG LUONG DIAMOND TRA VE
                SELECT mp.id as id,mp.name as name,
                                coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_return_id = mpwl.id
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name
                UNION ALL
                -- TINH TRONG LUONG DIAMOND BE, MAT
                SELECT mp.id as id,mp.name as name,
                                coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_lost_id = mpwl.id
                                AND sp.shipper = %s
                                AND sp.wo_lost_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id, mp.name
                ) as mrp
                GROUP BY mrp.id
                ) as diamond ON(diamond.id = mpwl.production_id)
                group by mp.name,mpwl.date_planned, mpwl.name,pp.coeff_24k,wk.percent, mp.metal_in_product
                having coalesce(sum(tab1.qty),0)
                +coalesce(sum(tab1.qty_24k),0)+ coalesce(sum(tab2.qty),0)
                +coalesce(sum(tab2.qty_24k),0)+ coalesce(sum(tab3.weight_ct),0)
                +coalesce(sum(tab3.weight_gr),0)+ coalesce(sum(tab4.weight_ct),0)
                +coalesce(sum(tab4.weight_gr),0)+ coalesce(sum(tab5.weight_gr),0)
                +coalesce(sum(tab6.weight_gr),0)<>0
                order by mp.name,mpwl.name ;

            ''' %(date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to)
        if employee_id:
            print sql
            cr.execute(sql)
            
            result = cr.dictfetchall()
            sequence =0

            arr.append({
                                'sequence':'Gold (Hao hụt vàng)',
                                'mrp_name': '-',
                                'line_name': '-',
                                'actual_date': '-',
                                'metal_delivery':'-',
                                'metal_24k_delivery': '-',
                                'metal_return': '-',
                                'metal_24k_return': '-',
                                'diamond_delivery_ct': '-',
                                'diamond_delivery_gr': '-',
                                'diamond_return_ct': '-',
                                'diamond_return_gr': '-',
                                'finish_delivery': '-',
                                'finish_return': '-',
                                'loss_weight': '-',
                                'loss': '-',
                                'loss_limit':'',
                                'loss_over':'',
                                'loss_24k':'',
                                'loss_limit_24k':'',
                                'loss_over_24k':'',
                                'net_weight':'-',
                                'percent':'-',
                                })


            sum_metal_delivery = 0
            sum_metal_24k_delivery= 0
            sum_metal_return =0
            sum_metal_24k_return =0
            sum_diamond_delivery_ct = 0
            sum_diamond_delivery_gr =0
            sum_diamond_return_ct =0
            sum_diamond_return_gr =0
            sum_finish_delivery=0
            sum_finish_return=0
            sum_loss_weight =0
            sum_loss =0
            sum_loss_limit = 0
            sum_loss_over = 0
            sum_loss_24k = 0
            sum_loss_limit_24k = 0
            sum_loss_over_24k = 0
            for item in result:

                arr.append({
                                'sequence':sequence,
                                'mrp_name': item['name'],
                                'line_name': item['line_name'],
                                'actual_date': item['actual_date'],
                                'metal_delivery': item['metal_delivery'],
                                'metal_24k_delivery': item['metal_24k_delivery'],
                                'metal_return': item['metal_return'],
                                'metal_24k_return': item['metal_24k_return'],
                                'diamond_delivery_ct': item['diamond_delivery_ct'],
                                'diamond_delivery_gr': item['diamond_delivery_gr'],
                                'diamond_return_ct': item['diamond_return_ct'],
                                'diamond_return_gr': item['diamond_return_gr'],
                                'finish_delivery': item['finish_delivery'],
                                'finish_return': item['finish_return'],
                                'loss_weight': round(float(item['loss_weight'] or 0.0),3),
                                'loss': round(float(item['loss'] or 0.0),3),
                                'loss_limit':round(float(item['loss_limit'] or 0.0),3),
                                'loss_over':round(float(item['loss_over'] or 0.0),3),
                                'loss_24k':round(float(item['loss_24k'] or 0.0),3),
                                'loss_limit_24k':round(float(item['loss_limit_24k'] or 0.0),3),
                                'loss_over_24k':round(float(item['loss_over_24k'] or 0.0),3),
                                'net_weight':round(float(item['net_weight'] or 0.0),3),
                                'percent':item['percent'] ,
                                })
                sum_metal_delivery +=item['metal_delivery']
                sum_metal_24k_delivery+=item['metal_24k_delivery']
                sum_metal_return +=item['metal_return']
                sum_metal_24k_return +=item['metal_24k_return']
                sum_diamond_delivery_ct +=item['diamond_delivery_ct']
                sum_diamond_delivery_gr += item['diamond_delivery_gr']
                sum_diamond_return_ct +=item['diamond_return_gr']
                sum_diamond_return_gr +=item['metal_delivery']
                sum_finish_delivery+=item['finish_delivery']
                sum_finish_return +=item['finish_return']
                sum_loss_weight+= round(float(item['loss_weight'] or 0.0),3)
                sum_loss +=round(float(item['loss'] or 0.0),3)
                sum_loss_limit += round(float(item['loss_limit'] or 0.0),3)
                sum_loss_over += round(float(item['loss_over'] or 0.0),3)
                sum_loss_24k += round(float(item['loss_24k'] or 0.0),3)
                sum_loss_limit_24k += round(float(item['loss_limit_24k'] or 0.0),3)
                sum_loss_over_24k += round(float(item['loss_over_24k'] or 0.0),3)
                sequence +=1

            arr.append({
                                'sequence':'-',
                                'mrp_name': 'Total',
                                'line_name': '-',
                                'actual_date': '-',
                                'metal_delivery': sum_metal_delivery,
                                'metal_24k_delivery':sum_metal_24k_delivery,
                                'metal_return': sum_metal_return,
                                'metal_24k_return': sum_metal_24k_return,
                                'diamond_delivery_ct': sum_diamond_delivery_ct,
                                'diamond_delivery_gr': sum_diamond_delivery_gr,
                                'diamond_return_ct': sum_diamond_return_ct,
                                'diamond_return_gr': sum_diamond_return_gr,
                                'finish_delivery': sum_finish_delivery,
                                'finish_return': sum_finish_return,
                                'loss_weight': sum_loss_weight,
                                'loss': sum_loss,
                                'loss_limit':sum_loss_limit,
                                'loss_over':sum_loss_over,
                                'loss_24k':sum_loss_24k,
                                'loss_limit_24k':sum_loss_limit_24k,
                                'loss_over_24k':sum_loss_over_24k,
                                'net_weight':'-',
                                'percent':'-',
                                })

    #================================== PLATINUM =============================================

        sql_platinum = '''
                SELECT
            mp.name,
            mpwl.date_planned actual_date,
            mpwl.name line_name,
            round(coalesce(sum(tab1.qty),0),3) as metal_delivery,
            coalesce(sum(tab1.qty_24k),0) as metal_24k_delivery,
            round(coalesce(sum(tab2.qty),0),3) as metal_return,
            coalesce(sum(tab2.qty_24k),0) as metal_24k_return,
            round(coalesce(sum(tab3.weight_ct),0),3) as diamond_delivery_ct,
            round(coalesce(sum(tab3.weight_gr),0),3) as diamond_delivery_gr,
            round(coalesce(sum(tab4.weight_ct),0),3) as diamond_return_ct,
            round(coalesce(sum(tab4.weight_gr),0),3) as diamond_return_gr,
            round(coalesce(sum(tab5.weight_gr),0),3) as finish_delivery,
            round(coalesce(sum(tab6.weight_gr),0),3) as finish_return,
            round(coalesce(sum(diamond.weight_gr),0),3) as diamond_weight,
              round(coalesce(sum(tab1.qty),0),3) -  round(coalesce(sum(tab2.qty),0),3)  +(round(coalesce(sum(tab5.weight_gr),0),3)
            -round(coalesce(sum(tab5.weight_gr)/sum(tab5.weight_gr)*sum(diamond.weight_gr),0),3)) -
            ((round(coalesce(sum(tab6.weight_gr),0),3)
            -round(coalesce(sum(tab6.weight_gr)/sum(tab6.weight_gr)*sum(diamond.weight_gr),0),3))) as loss_weight,
            pp.coeff_24k as coeff_24k,
           wk.percent as percent,
            mp.metal_in_product as net_weight,
            round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
            as loss,
            mp.metal_in_product * wk.percent /100
            as loss_limit,
            round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
             -  ( mp.metal_in_product * wk.percent /100)
             as loss_over,
           ( round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3))))
            * coeff_24k as loss_24k,
               ( mp.metal_in_product* wk.percent /100)
            *coeff_24k as loss_limit_24k,
             (round(coalesce(sum(tab1.qty),0),3)
            + (round(coalesce(sum(tab5.weight_gr),0),3) -  round(coalesce(sum(tab3.weight_gr),0),3) + round(coalesce(sum(tab4.weight_gr),0),3) )
            - ( round(coalesce(sum(tab2.qty),0),3) + (round(coalesce(sum(tab6.weight_gr),0),3)- round(coalesce(sum(tab3.weight_gr),0),3)+  round(coalesce(sum(tab4.weight_gr),0),3)))
             -  ( mp.metal_in_product* wk.percent /100))
            *coeff_24k as loss_over_24k
            from mrp_production_workcenter_line mpwl
             left join mrp_workcenter as wk on(wk.id = mpwl.workcenter_id)
            left join mrp_production as mp on(mp.id = mpwl.production_id)
            left join product_product as pp on (pp.id = mp.product_id)
            left join
            --- JOIN METAL DELIVERY  ---
                (SELECT mpwl.id as mpwl_id,    
                mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                AND pp.metal_class = 'platinum'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_delivery_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                AND sp.receiver =%s -- Employee
                                AND sp.wo_delivery_id IN (
                                 SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                
                                 --AND employee_id=1
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id,mpwl.name) as tab1 ON(tab1.mpwl_id = mpwl.id)
                left join ------------------- JOIN METAL RETURN -----------------------
                (SELECT mp.id mrp_id , mp.name mrp_name,mpwl.id as mpwl_id,mpwl.name mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                AND pp.metal_class = 'platinum'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_return_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                AND sp.shipper =%s -- Employee
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                 --AND employee_id=1
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id, mp.name ,mpwl.id,mpwl.name)
                as tab2 ON(tab2.mpwl_id = mpwl.id)

                LEFT JOIN
--- DIAMOND DELIVERY  ---
                (SELECT mp.id mp_id,mp.name mp_name,mpwl.id mpwl_id, mpwl.name mpwl_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_delivery_id
                                AND sp.receiver = %s
                                AND sp.wo_delivery_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name,mpwl.id, mpwl.name)
                as tab3 ON(tab3.mpwl_id = mpwl.id)

                LEFT JOIN(
                -- DIAMOND RETURN ---
                SELECT mpwl.id as mpwl_id, mpwl.name mpwl_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_return_id
                                AND sp.shipper = %s
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name
                ) as tab4 ON(tab4.mpwl_id = mpwl.id)
                --- FINISH DELIVERY ---
                LEFT JOIN
                (SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                AND pp.metal_class = 'platinum'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_delivery_id
                                AND sp.receiver = %s
                                AND sp.wo_delivery_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name)
                as tab5 ON(tab5.mpwl_id = mpwl.id)
                --- FINISH RETURN ---
                left join (
                SELECT mpwl.id as mpwl_id, mpwl.name as mpwl_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                AND pp.metal_class = 'platinum'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_return_id
                                AND sp.shipper = %s
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'   
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mpwl.id, mpwl.name
                ) as tab6 ON(tab6.mpwl_id = mpwl.id)
                left join
                --- DIAMOND IN FINISH PRODUCT ---
                (select mrp.id as id, coalesce(sum (weight_ct),0) as weight_ct, coalesce(sum(weight_gr),0) as weight_gr
                from(
                SELECT mp.id as id ,mp.name  as name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_delivery_id = mpwl.id
                                AND sp.wo_delivery_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                 )
                                 AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name
                UNION ALL
                -- TINH TRONG LUONG DIAMOND TRA VE
                SELECT mp.id as id,mp.name as name,
                                coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_return_id = mpwl.id
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id,mp.name
                UNION ALL
                -- TINH TRONG LUONG DIAMOND BE, MAT
                SELECT mp.id as id,mp.name as name,
                                coalesce (-SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(-SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                --AND sm.date >= to_date('%s','YYYY-MM-DD')
                                --AND sm.date < to_date('%s','YYYY-MM-DD')
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_lost_id = mpwl.id
                                AND sp.shipper = %s
                                AND sp.wo_lost_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'platinum'
                                 )
                                AND mpwl.date_planned >= to_date('%s','YYYY-MM-DD')
                AND mpwl.date_planned < to_date('%s','YYYY-MM-DD')
                GROUP BY mp.id, mp.name
                ) as mrp
                GROUP BY mrp.id
                ) as diamond ON(diamond.id = mpwl.production_id)
                group by mp.name,mpwl.date_planned, mpwl.name,pp.coeff_24k,wk.percent, mp.metal_in_product
                having coalesce(sum(tab1.qty),0)
                +coalesce(sum(tab1.qty_24k),0)+ coalesce(sum(tab2.qty),0)
                +coalesce(sum(tab2.qty_24k),0)+ coalesce(sum(tab3.weight_ct),0)
                +coalesce(sum(tab3.weight_gr),0)+ coalesce(sum(tab4.weight_ct),0)
                +coalesce(sum(tab4.weight_gr),0)+ coalesce(sum(tab5.weight_gr),0)
                +coalesce(sum(tab6.weight_gr),0)<>0
                order by mp.name,mpwl.name ;

            ''' %(date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  employee_id,
                  date_from,date_to)
        if employee_id:
            cr.execute(sql_platinum)
            print sql_platinum
            result_platinum = cr.dictfetchall()
            sequence =0
            arr.append({
                                'sequence':'Platinum (Hao hụt Platinum)',
                                'mrp_name': '-',
                                'line_name': '-',
                                'actual_date': '-',
                                'metal_delivery':'-',
                                'metal_24k_delivery': '-',
                                'metal_return': '-',
                                'metal_24k_return': '-',
                                'diamond_delivery_ct': '-',
                                'diamond_delivery_gr': '-',
                                'diamond_return_ct': '-',
                                'diamond_return_gr': '-',
                                'finish_delivery': '-',
                                'finish_return': '-',
                                 'loss_weight': '-',
                                'loss': '-',
                                'loss_limit':'',
                                'loss_over':'',
                                'loss_24k':'',
                                'loss_limit_24k':'',
                                'loss_over_24k':'',
                                'net_weight':'-',
                                'percent':'-',
                                })

            sum_metal_delivery = 0
            sum_metal_24k_delivery= 0
            sum_metal_return =0
            sum_metal_24k_return =0
            sum_diamond_delivery_ct = 0
            sum_diamond_delivery_gr =0
            sum_diamond_return_ct =0
            sum_diamond_return_gr =0
            sum_finish_delivery=0
            sum_finish_return=0
            sum_loss =0
            sum_loss_limit = 0
            sum_loss_over = 0
            sum_loss_24k = 0
            sum_loss_limit_24k = 0
            sum_loss_over_24k = 0
            for item in result_platinum:

                arr.append({
                                'sequence':sequence,
                                'mrp_name': item['name'],
                                'line_name': item['line_name'],
                                'actual_date': item['actual_date'],
                                'metal_delivery': item['metal_delivery'],
                                'metal_24k_delivery': item['metal_24k_delivery'],
                                'metal_return': item['metal_return'],
                                'metal_24k_return': item['metal_24k_return'],
                                'diamond_delivery_ct': item['diamond_delivery_ct'],
                                'diamond_delivery_gr': item['diamond_delivery_gr'],
                                'diamond_return_ct': item['diamond_return_ct'],
                                'diamond_return_gr': item['diamond_return_gr'],
                                'finish_delivery': item['finish_delivery'],
                                'finish_return': item['finish_return'],
                                'loss_weight': round(float(item['loss_weight'] or 0.0),3),
                                'loss': round(float(item['loss'] or 0.0),3),
                                'loss_limit':round(float(item['loss_limit'] or 0.0),3),
                                'loss_over':round(float(item['loss_over'] or 0.0),3),
                                'loss_24k':round(float(item['loss_24k'] or 0.0),3),
                                'loss_limit_24k':round(float(item['loss_limit_24k'] or 0.0),3),
                                'loss_over_24k':round(float(item['loss_over_24k'] or 0.0),3),
                                'net_weight':round(float(item['net_weight'] or 0.0),3),
                                'percent':item['percent'] ,
                                })
                sum_metal_delivery +=item['metal_delivery']
                sum_metal_24k_delivery+=item['metal_24k_delivery']
                sum_metal_return +=item['metal_return']
                sum_metal_24k_return +=item['metal_24k_return']
                sum_diamond_delivery_ct +=item['diamond_delivery_ct']
                sum_diamond_delivery_gr += item['diamond_delivery_gr']
                sum_diamond_return_ct +=item['diamond_return_gr']
                sum_diamond_return_gr +=item['metal_delivery']
                sum_finish_delivery+=item['finish_delivery']
                sum_finish_return +=item['finish_return']
                sum_loss +=round(float(item['loss'] or 0.0),3)
                sum_loss_limit += round(float(item['loss_limit'] or 0.0),3)
                sum_loss_over += round(float(item['loss_over'] or 0.0),3)
                sum_loss_24k += round(float(item['loss_24k'] or 0.0),3)
                sum_loss_limit_24k += round(float(item['loss_limit_24k'] or 0.0),3)
                sum_loss_over_24k += round(float(item['loss_over_24k'] or 0.0),3)
                sequence +=1

            arr.append({'sequence':'-',
                                'mrp_name': 'Total',
                                'line_name': '-',
                                'actual_date': '-',
                                'metal_delivery': sum_metal_delivery,
                                'metal_24k_delivery':sum_metal_24k_delivery,
                                'metal_return': sum_metal_return,
                                'metal_24k_return': sum_metal_24k_return,
                                'diamond_delivery_ct': sum_diamond_delivery_ct,
                                'diamond_delivery_gr': sum_diamond_delivery_gr,
                                'diamond_return_ct': sum_diamond_return_ct,
                                'diamond_return_gr': sum_diamond_return_gr,
                                'finish_delivery': sum_finish_delivery,
                                'finish_return': sum_finish_return,
                                'loss_weight': sum_loss_weight,
                                'loss': sum_loss,
                                'loss_limit':sum_loss_limit,
                                'loss_over':sum_loss_over,
                                'loss_24k':sum_loss_24k,
                                'loss_limit_24k':sum_loss_limit_24k,
                                'loss_over_24k':sum_loss_over_24k,
                                'net_weight':'-',
                                'percent':'-',
                                })


        return arr

wizard_hpusa_manufacturing_loss_report()

#===============================================================================
openoffice_report.openoffice_report(
     'report.manufacturing_loss_report_worker',
     'wizard.hpusa.manufacturing.loss.report',
     parser=wizard_hpusa_manufacturing_loss_report
 )

openoffice_report.openoffice_report(
     'report.manufacturing_loss_report_sumary',
     'wizard.hpusa.manufacturing.loss.report',
     parser=wizard_hpusa_manufacturing_loss_report
 )

openoffice_report.openoffice_report(
     'report.manufacturing_loss_worker_report_sumary',
     'wizard.hpusa.manufacturing.loss.report',
     parser=wizard_hpusa_manufacturing_loss_report
 )


#===============================================================================

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
