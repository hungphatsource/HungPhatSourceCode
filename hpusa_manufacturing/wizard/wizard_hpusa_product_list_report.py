
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

class wizard_hpusa_product_list_report(osv.osv_memory):
    _name = "wizard.hpusa.product.list.report"
    _columns = {
            'date_from': fields.date('Date From', required=True),
            'date_to': fields.date('Date To', required=True),
            'location_id': fields.many2one('stock.location', 'Location', required=True),
            'category_id': fields.many2one('product.category', 'Category'),
     }
    _defaults={
              'date_from': lambda *a: time.strftime('%Y-%m-01'),
              'date_to': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }

    def action_print(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_from','date_to','location_id','category_id'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hpusa.product.list.report'
        type = context.get('type_', '')
        if type == 'stock_in_out':
            datas['line'] = self.print_stock_in_out(cr, uid, res['date_from'], res['date_to'], res['location_id'] ,res['category_id'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'stock_in_out',
                'datas'         : datas,
           }
    # hpusa 08-07-2015
        elif type =='stock_in_out_diamond':
            datas['line'] = self.print_stock_in_out_diamonds(cr, uid, res['date_from'], res['date_to'], res['location_id'] ,res['category_id'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'stock_in_out_diamond',
                'datas'         : datas,
                }
        # hpusa 08-07-2015
        else:
            datas['line'] = self.stock_picking_detail(cr, uid, res['date_from'], res['date_to'], res['location_id'], res['category_id'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'stock_picking_detail',
                'datas'         : datas,
           }
    
    def stock_picking_detail(self, cr, uid, date_from, date_to, location_id, category_id):
        sql = '''
            SELECT sp.date, sp.name as sp_name, sp.note as sp_note, p.default_code, p.name_template as p_name, cate.name as categ_name, lo1.name as location, lo2.name as location_dest,
            receiver.name as receiver, shipper.name as shipper, sp.hp_transfer_type,
            CASE WHEN sp.origin IS NOT NULL THEN sp.origin ELSE sm.origin END as source,
            uom.name as uom, sm.product_qty,  sm.weight_mo, uom_weight.name as uom_weight, sm.note as sm_note
            FROM stock_move sm
            LEFT JOIN stock_picking sp ON(sp.id = sm.picking_id)
            LEFT JOIN product_product p ON(p.id = sm.product_id)
            LEFT JOIN product_template pt ON(pt.id = p.product_tmpl_id)
            LEFT JOIN product_category cate ON(cate.id = pt.categ_id)
            LEFT JOIN hr_employee em_shipper ON(em_shipper.id = sp.shipper)
            LEFT JOIN hr_employee em_receiver ON(em_receiver.id = sp.receiver)
            LEFT JOIN resource_resource shipper ON(shipper.id = em_shipper.resource_id)
            LEFT JOIN resource_resource receiver ON(receiver.id = em_receiver.resource_id)
            LEFT JOIN product_uom uom ON(uom.id = sm.product_uom)
            LEFT JOIN product_uom uom_weight ON(uom_weight.id = sm.weight_mo_unit)
            LEFT JOIN stock_location lo1 ON(lo1.id = sm.location_id)
            LEFT JOIN stock_location lo2 ON(lo2.id = sm.location_dest_id)
            WHERE (sm.location_id = %s OR sm.location_dest_id = %s) AND sm.date <= '%s' AND sm.date >= '%s'
         '''%(location_id[0],location_id[0], date_to, date_from)
        cr.execute(sql)
        result = cr.dictfetchall()
        print sql
        arr = []
        for item in result:
            arr.append({
                        'date': item['date'],
                        'sp_name': item['sp_name'],
                        'sp_note': item['sp_note'],
                        'default_code': item['default_code'],
                        'p_name': item['p_name'],
                        'categ_name': item['categ_name'],
                        'receiver': item['receiver'],
                        'shipper': item['shipper'],
                        'hp_transfer_type': item['hp_transfer_type'],
                        'source': item['source'],
                        'uom': item['uom'],
                        'product_qty': item['product_qty'],
                        'weight_mo': item['weight_mo'],
                        'uom_weight': item['uom_weight'],
                        'sm_note': item['sm_note'],
                        'location': item['location'],
                        'location_dest': item['location_dest'],
                        })
        return arr

    def print_stock_in_out(self, cr, uid, date_from, date_to, location_id, category):
        str_query = ''
        if category:
            str_query += '''WHERE cate.id = %s'''%(category[0])
            
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
            '''%(location_id[0], date_from,location_id[0], date_from, location_id[0], date_from, date_to, location_id[0], date_from, date_to, location_id[0], date_from, date_to,location_id[0], date_from, date_to,location_id[0], date_from, date_to, str_query)
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
        sum_qty_book=0
        sum_qty_book24k=0
        sum_qty_real=0
        sumqty_real_24k=0
    
        for item in result:
            if float(item['qty_adjust']>=0):
                qty_in = item['qty_in']+item['qty_adjust']
                qty_out =item['qty_out']
            else:
                qty_out =  item['qty_out'] +item['qty_adjust']   
                qty_in = item['qty_in']
                
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
                        'end_book': item['end_book'],
                        'endbook_24k': item['endbook_24k'],
                        'qty_real': item['qty_real'],
                        'real_24k':  item['real_24k'],
                        })
            # hpusa 13-07-2015
            sum_qty_first+= item['qty_first']
            sum_qty_24k += item['qty_24k']
            sum_qty_in +=item['qty_in']
            sumqty_out +=item['qty_out']
            sumqty_loss += item['qty_lost']
            sum_qty_adjust +=item['qty_adjust']
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
                        'end_book': round(sum_qty_book,2),
                        'endbook_24k': round(sum_qty_book24k,2),
                        'qty_real': round(sum_qty_real,2),
                        'real_24k':  round(sumqty_real_24k,2),
                        })
        # hpusa 13-07-2015

        return arr

    #hpusa 08-07-2015

    def print_stock_in_out_diamonds(self, cr, uid, date_from, date_to, location_id, category):
        print 'Start get information'
        cate_arr=[]
        cate_arr.append(category[0])
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
                            SELECT _third.product_id, SUM(_third.qty) as qty, sum(_third.wt) as wt FROM(
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
                            ) as _third
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
                '''%(location_id[0], date_from,location_id[0], date_from, location_id[0], date_from, date_to, location_id[0],date_from, date_to, location_id[0],date_from, date_to, location_id[0], date_from, date_to, location_id[0], date_from, date_to,location_id[0], date_from, date_to,location_id[0],date_from, date_to,location_id[0],date_from, date_to, str_query)
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
                                'quality': '-',
                                'quality_description': '-',
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
                                'qty_stock':  '-',
                                'wt_stock':  '-',
                                'qty_adjust':  '-',
                                'wt_adjust':  '-',
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
            # hpusa 13-07-2015

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


openoffice_report.openoffice_report(
    'report.stock_picking_detail',
    'wizard.hpusa.product.list.report',
    parser=wizard_hpusa_product_list_report
)

openoffice_report.openoffice_report(
    'report.stock_in_out',
    'wizard.hpusa.report',
    parser=wizard_hpusa_product_list_report
)

# hpusa 08-07-2015
openoffice_report.openoffice_report(
    'report.stock_in_out_diamond',
    'wizard.hpusa.report',
    parser=wizard_hpusa_product_list_report
)
# hpusa 08-07-2015


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
