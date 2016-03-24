
from openerp.osv import fields, osv
import time
from datetime import datetime
from dateutil import relativedelta

class default_stock_report(osv.osv):
    
    _name="hpusa.report.configuration"
    _inherit = ['mail.thread', 'ir.needaction_mixin'] 
    _description="Hpusa Report  Configuration"
    
    _columns={
              'name':fields.char('Name'),
              'stock':fields.many2one('stock.location','Stock'),
              'production':fields.many2one('stock.location','Production Stock'),
              'raw_category':fields.many2one('product.category','Raw Material'),
              'diamond_category': fields.many2one('product.category','Diamonds'),
                        
              }
default_stock_report()

class inventory_report(osv.osv):
    
    _name="hpusa.report.inventory"
    _description="Inventory Report"
    _inherit = ['mail.thread', 'ir.needaction_mixin'] 
    _columns={
            'name':fields.char('Name',required=True),
            'year_id': fields.many2one('year.configuration','Year',required=True),
            'period': fields.selection([('01','January'),
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
                                       ],'Period',required=True),
            'date_start': fields.date('Date Start',required=True),
            'date_end': fields.date('Date End',required=True),
            'company_id': fields.many2one('res.company','Company'),
            'gold_category': fields.many2one('product.category','Gold Category',required=True),
            'diamond_category': fields.many2one('product.category','Diamond Category',required=True),
            'main_stock_id':fields.many2one('stock.location','Stock',required=True),
            'production_stock_id':fields.many2one('stock.location','Production Stock',required=True),

            'gold_start': fields.float('Gold Start'),
            'gold_in':fields.float('Gold In'),
            'gold_out':fields.float('Gold Out'),
            'gold_pending':fields.float('Gold Pending'),
            'gold_finish':fields.float('Gold Finished'),
            'gold_loss': fields.float('Loss Weight'),
            'gold_loss_limit':fields.float('Loss Limit'),
            'gold_loss_over':fields.float('Loss Over'),
            'gold_ship_to_us':fields.float('Ship to US'),  
            'gold_end_phyical': fields.float('Balance Gold Physical'),
            'gold_end_erp': fields.float('Balance Gold End(Book)', readonly=True, status={'open': [('readonly', False)]}),
            'diff_gold': fields.float('Diffence Gold'),
        
            'pt_start': fields.float('PT Start'),
            'pt_in':fields.float('PT In'),
            'pt_out':fields.float('PT Out'),
            'pt_pending':fields.float('PT Pending'),
            'pt_finish':fields.float('PT Finished'),
            'pt_loss': fields.float('PT Weight'),
            'pt_loss_limit':fields.float('PTLimit'),
            'pt_loss_over':fields.float('PT Over'),
            'pt_ship_to_us':fields.float('PT to US'),  
            'pt_end_phyical': fields.float('Balance PT Physical'),
            'pt_end_erp': fields.float('Balance PT End(Book)', readonly=True, status={'open': [('readonly', False)]}),
            'diff_pt': fields.float('Diffence PT'),
            
            
            'diamond_start': fields.float('Diamond Start'),
            'diamond_in':fields.float('Diamond In'),
            'diamond_out':fields.float('Diamond Out'),
            'diamond_pending':fields.float('Diamond Pending'),
            'diamond_finish':fields.float('Diamond Finished'),
            'diamond_loss': fields.float('Diamond Weight'),
            'diamond_loss_limit':fields.float('Diamond Limit'),
            'diamond_loss_over':fields.float('Diamond Over'),
            'diamond_ship_to_us':fields.float('Diamond to US'),  
            'diamond_end_physical': fields.float('Diamond End Physical'),
            'diamond_end_erp': fields.float('Balance End Diamond(Book)', readonly=True, status={'open': [('readonly', False)]}),
            'diff_diamond': fields.float('Diffence Diamond'),
            
            'status': fields.selection([('open','Open'),('closed','Closed')],'Status', required=True,track_visibility='onchange'),
               

               'gold_los_limit_allow':fields.float('Loss Percent'),                                      
              }
    
    _defaults={  
              'status': 'open',
              'date_start': lambda *a: time.strftime('%Y-%m-01'),
              'date_end': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
              'year_id':1,  
              'gold_los_limit_allow':0.03,
              
    }
    
    _track = {
        'status': {
            'hpusa_warehouse_material_report.mt_tract_new': lambda self, cr, uid, obj, ctx=None: obj['status'] in ['open', 'closed'],
                }
            }
    
    def update_data(self,cr,uid,ids,context):
        
        this = self.browse(cr, uid, ids[0], context)
        date_start = this.date_start
        date_end = str(datetime.strptime(this.date_end,'%Y-%m-%d') + relativedelta.relativedelta(days=1))[:10]
        
        gold_book=0
        diff_gold = 0
        
        diamond_book = 0
        diamond_physical = this.diamond_end_physical
        diff_diamond =0
        gold_real_24k =0
        diamond_real =0
        
        main_stock_id = this.main_stock_id.id
        production_stock_id = this.production_stock_id.id
        gold_category = this.gold_category.id
        diamond_category = this.diamond_category.id
        
        gold_book += self.request_stock_report_rawmaterrial(cr,uid,date_start,date_end,main_stock_id,gold_category)
        gold_book += self.request_stock_report_rawmaterrial(cr,uid,date_start,date_end,production_stock_id,gold_category)
        
        gold_real_24k += self.request_stock_report_rawmaterrial_real(cr,uid,date_start,date_end,main_stock_id,gold_category)
        gold_real_24k += self.request_stock_report_rawmaterrial_real(cr,uid,date_start,date_end,production_stock_id,gold_category)
        
        diff_gold = gold_real_24k- gold_book
        diamond_book += self.request_stock_in_out_diamonds(cr,uid,date_start,date_end,main_stock_id,diamond_category)
        diamond_real += self.request_stock_in_out_diamonds_real(cr,uid,date_start,date_end,main_stock_id,diamond_category)
        
        diff_diamond = diamond_real-diamond_book
        arr = self.request_loss_month(cr, uid, date_start, date_end)
        weight_loss = 0
        gold_loss_limit = 0
        gold_loss_over = 0
        for item in arr :
            weight_loss = item['weight_loss']
            gold_loss_limit = item['loss_limit']
            gold_loss_over = item['loss_over']
        
        gold_start = 0
        gold_in = 0
        gold_out =0
        gold_pending = 0 
        gold_finish = 0
        gold_ship_to_us = 0
      
        
        category =[]
        category.append(gold_category)
        main_stock = []
        main_stock.append(main_stock_id)
        production_stock =[]
        production_stock.append(production_stock_id)
        
        result_main =   self.print_stock_in_out( cr, uid, date_start, date_end, main_stock, category)
        
        result_production = self.print_stock_in_out( cr, uid, date_start, date_end, production_stock, category)
        
        #=== Lay du lieu dau ky ===#
        if result_main:
            gold_start+= float(result_main[0]['qty_24k'] or 0)
            gold_in += float(result_main[0]['qty_in'] or 0)
            gold_out += float(result_main[0]['qty_out'] or 0)
        
        if result_production:
            gold_start+= float(result_production[0]['qty_24k'] or 0)
            gold_in += float(result_production[0]['qty_in'] or 0)
            gold_out += float(result_production[0]['qty_out'] or 0)
            
        #=== Get Manufacturing Order Loss ===#
            
        mo_info = self.export_manufacturing_loss_sumary(cr,uid,date_start,date_end)
        
        if mo_info:
            gold_finish += mo_info[0]['net_weight']
            gold_pending = gold_out- gold_in -  gold_finish - weight_loss
            ship_infor =  self.export_manufacturing_loss_sumary_ship(cr,uid,date_start,date_end)
            gold_ship_to_us =  ship_infor[0]['net_weight']
            
        self.write(cr, uid, ids, {
                                'gold_end_erp': gold_book,
                                'gold_end_phyical':gold_real_24k, 
                                'diff_gold': diff_gold,
                                'diff_diamond':diff_diamond,
                                'diamond_end_erp': diamond_book,
                                'diamond_end_physical': diamond_real, 
                                'gold_loss': weight_loss,
                                'gold_start': gold_start,
                                'gold_in':gold_in,
                                'gold_out':gold_out,
                                'gold_pending':gold_pending,
                                'gold_finish':gold_finish,
                                'gold_loss_limit':gold_loss_limit,
                                'gold_loss_over':gold_loss_over,
                                'gold_ship_to_us':gold_ship_to_us,    
                                  }, context)
   
        print date_start + '  ' +date_end 
        
        #Start get info Platinum#
        pt_in_out = self.get_stock_in_out_platinum(cr, uid, date_start, date_end, main_stock, category )
        pt_loss_get = self.export_manufacturing_loss_platinum (cr,uid,date_start,date_end)
        pt_loss_ship= self.export_manufacturing_loss_platinum_ship(cr,uid,date_start,date_end)
        
        pt_start = 0
        pt_in = 0
        pt_out = 0
        pt_pending = 0
        pt_finish =0 
        pt_loss = 0 
        pt_loss_limit = 0 
        pt_loss_over = 0
        pt_ship_to_us = 0
        pt_end_phyical = 0
        pt_end_erp = 0
        diff_pt = 0
        
        pt_start = pt_in_out[0]['qty_first']
        pt_in = pt_in_out[0]['qty_in']
        pt_out = pt_in_out[0]['qty_out']
        pt_pending = pt_in_out[0]['qty_out'] -pt_loss_get[0]['net_weight'] - pt_in_out[0]['qty_lost'] 
        pt_finish =pt_loss_get[0]['net_weight'] 
       
        pt_loss_limit = pt_loss_get[0]['net_weight'] * this.gold_los_limit_allow 
        pt_loss_over =  pt_loss_get[0]['loss_weight']
        pt_ship_to_us = pt_loss_ship[0]['net_weight']
        pt_end_phyical = pt_in_out[0]['qty_real']
        pt_end_erp = pt_in_out[0]['end_book']  
        diff_pt = pt_in_out[0]['qty_adjust'] 
        pt_loss = pt_in_out[0]['qty_lost'] 
        self.write(cr, uid, ids, {
                                'pt_start' :pt_start,
                                'pt_in':pt_in,
                                'pt_out':  pt_out, 
                                'pt_pending':pt_pending, 
                                'pt_finish':  pt_finish ,
                                'pt_loss': pt_loss  ,
                                'pt_loss_limit':  pt_loss_limit ,
                                'pt_loss_over':   pt_loss_over ,
                                'pt_ship_to_us':  pt_ship_to_us ,
                                'pt_end_phyical':  pt_end_phyical ,
                                'pt_end_phyical': pt_end_erp,
                                'diff_pt' :diff_pt 
                                       
                                  }, context)
        
        
        #Start get info Diamond#
        dia_category = []
        dia_category.append(diamond_category)
        
        diamond_get =self.get_stock_in_out_diamonds(cr, uid,date_start , date_end, main_stock, dia_category)
        
        
        diamond_start = diamond_get[0]['wt_first']
        diamond_in = diamond_get[0]['wt_in']
        diamond_out = diamond_get[0]['wt_out']
        diamond_pending = diamond_get[0]['wt_out'] - diamond_get[0]['wt_in'] - mo_info[0]['diamond_weight']
        diamond_finish = mo_info[0]['diamond_weight']
        
        diamond_loss = diamond_get[0]['wt_lost']
        diamond_loss_limit = 0
        diamond_loss_over = 0
        diamond_ship_to_us = diamond_get[0]['wt_ship']
        diamond_end_physical = diamond_get[0]['wt_stock']
        diamond_end_erp = diamond_get[0]['wt_endbook']
        diff_diamond = diamond_get[0]['wt_adjust']
       
        self.write(cr, uid, ids, {
                                'diamond_start' :diamond_start,
                                'diamond_in':diamond_in,
                                'diamond_out':  diamond_out, 
                                'diamond_pending':diamond_pending, 
                                'diamond_finish':  diamond_finish ,
                                'diamond_loss': diamond_loss  ,
                                'diamond_loss_limit':  diamond_loss_limit ,
                                'diamond_loss_over':   diamond_loss_over ,
                                'diamond_ship_to_us':  diamond_ship_to_us ,
                                'diamond_end_physical':  diamond_end_physical ,
                                'diamond_end_erp': diamond_end_erp, 
                                'diff_diamond':diff_diamond ,       
                                  }, context)
         
        return True
    
    
    def get_stock_in_out_diamonds(self, cr, uid, date_from, date_to, location_id, category):
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

    def get_stock_in_out_platinum(self, cr, uid, date_from, date_to, location_id, category):
        str_query = ''
        if category:
            str_query += '''AND cate.id = %s'''%(category[0])
            
        sql = '''
                SELECT p.id, MAX(pt.list_price) as list_price
                , p.default_code
                , p.name_template as name
                , uom.name as uom
                , coalesce(MAX(tab.qty),0) as qty_first              
                , coalesce(MAX(tab2.qty),0)  as qty_in                 
                , coalesce(MAX(tab3.qty),0) as qty_out
                , coalesce(MAX(tab4.qty),0) as qty_lost
                , coalesce(MAX(tab_adjust.qty),0) as qty_adjust
                , coalesce(MAX(tab.qty),0)  + coalesce(MAX(tab2.qty),0) - coalesce(MAX(tab_adjust.qty),0) -coalesce(MAX(tab3.qty),0)  as end_book
                , (coalesce(MAX(tab.qty),0)  + coalesce(MAX(tab2.qty),0)  - coalesce(MAX(tab_adjust.qty),0) -coalesce(MAX(tab3.qty),0))*coalesce(p.coeff_24k,0) as endbook_24k
                , coalesce(MAX(tab.qty),0) + coalesce(MAX(tab2.qty),0)  -coalesce(MAX(tab3.qty),0) as qty_real
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
                    WHERE p.metal_class = 'platinum'
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
                
            
            # hpusa 13-07-2015
            sum_qty_first+= item['qty_first']
           
            sum_qty_in +=item['qty_in']
            sumqty_out +=item['qty_out']
            sumqty_loss += item['qty_lost']
            sum_qty_adjust +=item['qty_adjust']
            sum_qty_book +=item['end_book']
            sum_qty_book24k +=item['endbook_24k']
            sum_qty_real +=item['qty_real']
            


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

    def export_manufacturing_loss_platinum(self,cr,uid,date_from,date_to):
        
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
            mrp.metal_in_product  as net_weight, 
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
        
        
        sequence =0
        
        for item in result:
            
            sum_metal_delivery += round(float(item['metal_delivery'] or 0.0),2)
            sum_metal_return +=round(float(item['metal_return'] or 0.0),2)
            sum_meta_used +=round(float(item['metal_used'] or 0.0),2) 
            sum_finished_weight +=round(float(item['finished_weight'] or 0.0),2)
            sum_net_weight += round(float(item['net_weight'] or 0.0),2)
            sum_diamond_weight +=round(float(item['diamond_weight'] or 0.0),2)
            sum_loss_weight +=round(float(item['loss_weight'] or 0.0),2)
           
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
   
    def export_manufacturing_loss_platinum_ship(self,cr,uid,date_from,date_to):
        
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
            mrp.metal_in_product  as net_weight, 
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
            AND mrp.company_id <> 3
      
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
        
        
        sequence =0
        
        for item in result:
            
            sum_metal_delivery += round(float(item['metal_delivery'] or 0.0),2)
            sum_metal_return +=round(float(item['metal_return'] or 0.0),2)
            sum_meta_used +=round(float(item['metal_used'] or 0.0),2) 
            sum_finished_weight +=round(float(item['finished_weight'] or 0.0),2)
            sum_net_weight += round(float(item['net_weight'] or 0.0),2)
            sum_diamond_weight +=round(float(item['diamond_weight'] or 0.0),2)
            sum_loss_weight +=round(float(item['loss_weight'] or 0.0),2)
          
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
     
    def request_stock_report_rawmaterrial(self, cr, uid, month_from, month_to, stock_ids, category):
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
            '''%(stock_ids, month_from,stock_ids, month_from, stock_ids, month_from, month_to, stock_ids, month_from, month_to, stock_ids, month_from, month_to,stock_ids, month_from, month_to,stock_ids, month_from, month_to, str_query)
        cr.execute(sql)
        print sql
        result = cr.dictfetchall()
         
        sum_qty_24k=0
        sum_stock_24k=0
       
        
        for item in result:
           
            if item['coeff_24k']:
                #qty_24k = item['qty_first'] * item['coeff_24k']
                #stock_24k = (item['qty_first'] + item['qty_in'] - item['qty_out']) * item['coeff_24k']
                sum_qty_24k += item['end_book']
                sum_stock_24k +=item['endbook_24k']
               
        return sum_stock_24k

    def request_stock_report_rawmaterrial_real(self, cr, uid, month_from, month_to, stock_ids, category):
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
            '''%(stock_ids, month_from,stock_ids, month_from, stock_ids, month_from, month_to, stock_ids, month_from, month_to, stock_ids, month_from, month_to,stock_ids, month_from, month_to,stock_ids, month_from, month_to, str_query)
        cr.execute(sql)
        print sql
        result = cr.dictfetchall()
         
        sum_qty_24k=0
        sum_stock_24k=0
       
        
        for item in result:
            if item['coeff_24k']:
                #qty_24k = item['qty_first'] * item['coeff_24k']
                #stock_24k = (item['qty_first'] + item['qty_in'] - item['qty_out']) * item['coeff_24k']
                sum_qty_24k += item['qty_real']
                sum_stock_24k +=item['real_24k']
               
        return sum_stock_24k
    
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
                    
        total_wt_stock = 0
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
                            SELECT product_id
                            , coalesce(SUM(product_qty),0) as qty
                            ,coalesce(SUM(weight_mo),0) as wt
                            FROM stock_move
                            WHERE location_dest_id = %s
                            AND date >= '%s'
                            AND date <= '%s' AND state = 'done'
                            AND location_id <>  location_dest_id
                            GROUP BY product_id
                            ) as tab2 ON(tab2.product_id =  p.id)

                        -- Xuat
                        LEFT JOIN (
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
                '''%(location_id, date_from,location_id, date_from, location_id, date_from, date_to, location_id, date_from, date_to, location_id, date_from, date_to,location_id, date_from, date_to,location_id, date_from, date_to,location_id, date_from, date_to, str_query)
            cr.execute(sql)
            print sql
            result = cr.dictfetchall() 
           
        # hpusa 13-07-2015
            sum_wt_stock=0
            
              
            for item in result:
                
                if float(item['qty_adjust']>=0):
                    wt_in= item['wt_in']-item['wt_adjust']
                    wt_out =item['wt_out']
                else:
                    wt_in= item['wt_in']
                    wt_out =item['wt_out']-item['wt_adjust']
                    
         # hpusa 13-07-2015
                sum_wt_stock += item['wt_first'] + wt_in -wt_out
                
                        
            total_wt_stock += sum_wt_stock
           
  
        print 'End get information'    
        return total_wt_stock
    
    def request_stock_in_out_diamonds_real(self, cr, uid, date_from, date_to, location_id, category):
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
                    
        total_wt_stock = 0
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
                            SELECT product_id
                            , coalesce(SUM(product_qty),0) as qty
                            ,coalesce(SUM(weight_mo),0) as wt
                            FROM stock_move
                            WHERE location_dest_id = %s
                            AND date >= '%s'
                            AND date <= '%s' AND state = 'done'
                            AND location_id <>  location_dest_id
                            GROUP BY product_id
                            ) as tab2 ON(tab2.product_id =  p.id)

                        -- Xuat
                        LEFT JOIN (
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
                '''%(location_id, date_from,location_id, date_from, location_id, date_from, date_to, location_id, date_from, date_to, location_id, date_from, date_to,location_id, date_from, date_to,location_id, date_from, date_to,location_id, date_from, date_to, str_query)
            cr.execute(sql)
            print sql
            result = cr.dictfetchall() 
           
        # hpusa 13-07-2015
            sum_wt_stock=0
            
              
            for item in result:
                
                if float(item['qty_adjust']>=0):
                    wt_in= item['wt_in']-item['wt_adjust']
                    wt_out =item['wt_out']
                else:
                    wt_in= item['wt_in']
                    wt_out =item['wt_out']-item['wt_adjust']
                    
         # hpusa 13-07-2015
                sum_wt_stock += (item['wt_first'] + item['wt_in']  - item['wt_out'])
                
                        
            total_wt_stock += sum_wt_stock
           
  
        print 'End get information'    
        return total_wt_stock
          
    def request_loss_month(self,cr,uid,date_from,date_to):
        weight_loss= 0
        loss_limit = 0
        loss_over = 0
        
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
                                AND sp.wo_delivery_id IN (
                                 SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                
                                 --AND employee_id=1
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 --AND employee_id=1
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                                AND sp.wo_delivery_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                                AND sp.wo_delivery_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                                AND sp.wo_return_id IN (
                                  SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')   
                                 )

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
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                                AND sp.wo_lost_id IN (
                                SELECT mpwl.id
                                 FROM mrp_production_workcenter_line mpwl,
                                 mrp_production mp,
                                 product_product pp
                                 WHERE mp.id = mpwl.production_id
                                 AND mp.product_id = pp.id
                                 AND pp.metal_class = 'gold'
                                 AND mp.mo_date >= to_date('%s','YYYY-MM-DD')
                                         AND mp.mo_date < to_date('%s','YYYY-MM-DD')
                                 )
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
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to,
                  date_from,date_to)
            
        cr.execute(sql)
        print sql
        arr = []
        results = cr.dictfetchall()
        if len(results)>=1:
            for result in results:
                if(result['loss_24k']!=None):
                    weight_loss += round(float(result['loss_24k']or 0.0),3)
                    loss_limit += round(float(result['loss_limit_24k']or 0.0),3)
                    loss_over += round(float(result['loss_over_24k']or 0.0),3)
        
            arr.append({'weight_loss':weight_loss,
                        'loss_limit': loss_limit,
                        'loss_over':loss_over,
                        })
        
        return  arr

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
                , coalesce(MAX(tab2.qty),0) * coalesce(p.coeff_24k,0)   as qty_in                 
                , coalesce(MAX(tab3.qty),0) * coalesce(p.coeff_24k,0) as qty_out
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
                
#             arr.append({
#                         'default_code': item['default_code'],
#                         'name': item['name'],
#                         'uom': item['uom'],
#                         'coeff_24k': item['coeff_24k'],
#                         'qty_first': item['qty_first'],
#                         'qty_24k': item['qty_24k'],
#                         'qty_in': item['qty_in'],
#                         'qty_out': item['qty_out'],
#                         'qty_lost': item['qty_lost'],
#                         'qty_adjust': item['qty_adjust'],
#                         'end_book': item['end_book'],
#                         'endbook_24k': item['endbook_24k'],
#                         'qty_real': item['qty_real'],
#                         'real_24k':  item['real_24k'],
#                         })
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
            mrp.metal_in_product *pp.coeff_24k as net_weight, 
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
        
        
        sequence =0
        
        for item in result:
            
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
        return arr

    def export_manufacturing_loss_sumary_ship(self,cr,uid,date_from,date_to):
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
            mrp.metal_in_product *pp.coeff_24k as net_weight, 
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
            AND mrp.company_id <> 3
      
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
        
        
        sequence =0
        
        for item in result:
            
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
        return arr
        
inventory_report()