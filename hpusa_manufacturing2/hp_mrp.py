import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime
from openerp.tools import float_compare
#from test.badsyntax_future3 import result

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _get_mo(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for production_id in ids:
            wo_state=''
            wo_name=''
            wo_id=0
            wo_employee=0
            if production_id:
                i = 0
                flag = False
                production_obj = self.browse(cr, uid, production_id)
                if production_obj.workcenter_lines:
                    wc_end =  production_obj.workcenter_lines[len(production_obj.workcenter_lines)-1].id
                    flag = False
                    for wo_line in production_obj.workcenter_lines:
                        #print wo_line.id
                        if wo_line.state != 'done' or wc_end == wo_line.id:
                            if flag == False:
                                wo_id = wo_line.workcenter_id.id
                                wo_name = wo_line.workcenter_id.name
                                wo_state = wo_line.state
                                wo_employee = wo_line.employee_id.id

                                #wo_name= wo_line.workcenter_id.name #hpusa configure
                                flag = True
                                break
            # hpusa start Configure
            if str(wo_state) =='draft':
                wo_state ='Draft'
            elif str(wo_state)=='waiting_director':
                wo_state ='Waiting Director'
            elif str(wo_state)=='startworking':
                wo_state ='Inprogress'
            elif str(wo_state)=='done':
                wo_state ='Done'
            elif str(wo_state)=='cancel':
                wo_state ='Cancel'
            elif str(wo_state)=='pause':
                wo_state ='Pending'
            # HPUSA Configure 23-04-2015
            #self.write(cr, uid, [record.id], {'work_order': str(wo_name), 'work_order_status': str(wo_state)}, context=context) # hpusa configure
            #cr.commit() # hpusa configure
            result[production_id] = {'wo_id': wo_id}
            self.write(cr, uid, [production_id],{'wo_view': wo_name, 'state_view': wo_state,'employee_id':wo_employee })
            cr.commit()
        return result

    def update_loss(self,cr,uid,ids,context=None ):

        for mrp in self.browse(cr, uid, ids):

            sql ="""

            SELECT
            mrp.id, mrp.name,
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
            round(coalesce(sum(tab7.weight_gr),0),3) as diamond_loss_weight,
            round(coalesce(sum(tab7.qty),0),3) as diamond_loss_qty,
            pp.coeff_24k as coeff_24k,
            coalesce(sum(tab1.qty_24k),0) as total_metal24k_delivery,
            coalesce((coalesce(sum(tab2.qty_24k),0)
            +((round(coalesce(sum(tab6.weight_gr),0),3) -round(coalesce(sum(tab5.weight_gr),0),3)
            -round(coalesce(sum(diamond.weight_gr),0),3))*pp.coeff_24k) ) ) as total_24k_return
            ,coalesce( (coalesce(sum(tab5.weight_gr),0)-round(coalesce(sum(diamond.weight_gr),0),3)) *pp.coeff_24k ,0)  as sub_total_24k_return
            from mrp_production mrp
            left join product_product as pp On(pp.id = mrp.product_id)
            left join
            --- JOIN METAL DELIVERY  --------------------------------------------------------
                (
                SELECT mp.id as mp_id,
                mp.name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='delivery'
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                --AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_delivery_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                --AND sp.receiver =1 -- Employee
                                AND sp.wo_delivery_id IN (
                     SELECT mpwl.id as id
                     FROM mrp_production_workcenter_line mpwl
                     where mpwl.production_id =%s
                                 --AND employee_id=1
                                 )
                GROUP BY mp.id,mp.name) as tab1 ON(tab1.mp_id = mrp.id)
                left join ------------------- JOIN METAL RETURN ----------------------------------------------
                (
                SELECT mp.id mrp_id , mp.name mrp_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.product_qty * coeff_24k),0) as qty_24k
                                FROM stock_move sm,
                                stock_picking sp,
                                product_product pp,
                                mrp_production_workcenter_line mpwl,
                                mrp_production mp
                                WHERE sp.hp_transfer_type='return'
                                AND sm.state = 'done'
                                AND pp.hp_type ='metal'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND sp.wo_return_id = mpwl.id
                                AND mpwl.production_id = mp.id
                                AND sp.wo_return_id IN (
                                SELECT mpwl.id as id
                     FROM mrp_production_workcenter_line mpwl
                     where mpwl.production_id =%s
                                 )
                GROUP BY mp.id, mp.name
                )
                as tab2 ON(tab2.mrp_id = mrp.id)
                LEFT JOIN
--- DIAMOND DELIVERY  -------------------------------------------------------------------------------
                (SELECT mp.id mp_id,mp.name mp_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_delivery_id
                                --AND sp.receiver = 1
                                AND sp.wo_delivery_id IN (
                                 SELECT mpwl.id as id
                     FROM mrp_production_workcenter_line mpwl
                     where mpwl.production_id =%s
                                 )
                GROUP BY mp.id,mp.name
                )
                as tab3 ON(tab3.mp_id = mrp.id)
                LEFT JOIN(
                -- DIAMOND RETURN -------------------------------------------
                SELECT mp.id as mp_id, mp.name mp_name,
                                coalesce (SUM(sm.weight_mo),0) as weight_ct ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_return_id
                                --AND sp.receiver = 1
                                AND sp.wo_return_id IN (
                                 SELECT mpwl.id as id
                     FROM mrp_production_workcenter_line mpwl
                     where mpwl.production_id =%s
                                 )
                GROUP BY mp.id, mp.name
                ) as tab4 ON(tab4.mp_id = mrp.id)
                -- LOSS DIAMOND INFOMATION------------------------------------------------------------
                LEFT JOIN(
                SELECT mp.id as mp_id, mp.name mp_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo /5),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='lost'
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND mpwl.id = sp.wo_lost_id
                                --AND sp.receiver = 1
                                AND sp.wo_return_id IN (
                    SELECT mpwl.id as id
                    FROM mrp_production_workcenter_line mpwl
                    where mpwl.production_id =%s
                                 )
                GROUP BY mp.id, mp.name

                ) as tab7 ON(tab7.mp_id = mrp.id)
                --- FINISH DELIVERY ------------------------------------------
                LEFT JOIN
                (
                SELECT mp.id as mp_id, mp.name as mp_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='delivery'
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                --AND pp.metal_class = 'gold'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_delivery_id
                                --AND sp.shipper = 1
                                AND sp.wo_delivery_id IN (
                                 SELECT mpwl.id as id
                    FROM mrp_production_workcenter_line mpwl
                    where mpwl.production_id =%s
                                 )
                GROUP BY mp.id, mp.name)
                as tab5 ON(tab5.mp_id = mrp.id)
                --- FINISH RETURN ---
                left join (
                SELECT mp.id as mp_id, mp.name as mp_name,
                                coalesce (SUM(sm.product_qty),0) as qty ,
                                coalesce(SUM(sm.weight_mo),0) as weight_gr
                                FROM stock_move sm ,
                                stock_picking sp,
                                product_product pp,
                                mrp_production mp,
                                mrp_production_workcenter_line mpwl
                                WHERE sp.hp_transfer_type='return'
                                AND sm.state = 'done'
                                AND pp.hp_type ='finish_product'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id= mpwl.production_id
                                AND mpwl.id= sp.wo_return_id
                                --AND sp.shipper = 1
                                AND sp.wo_return_id IN (
                                 SELECT mpwl.id as id
                    FROM mrp_production_workcenter_line mpwl
                    where mpwl.production_id =%s
                                 )
                GROUP BY mp.id, mp.name
                ) as tab6 ON(tab6.mp_id = mrp.id)
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
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_delivery_id = mpwl.id
                                AND sp.wo_delivery_id IN (
                                 SELECT mpwl.id as id
                    FROM mrp_production_workcenter_line mpwl
                    where mpwl.production_id =%s
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
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_return_id = mpwl.id
                                AND sp.wo_return_id IN (
                     SELECT mpwl.id as id
                    FROM mrp_production_workcenter_line mpwl
                    where mpwl.production_id =%s
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
                                AND sm.state = 'done'
                                AND pp.hp_type ='diamonds'
                                AND sm.product_id =pp.id
                                AND sm.picking_id= sp.id
                                AND mp.id = mpwl.production_id
                                AND sp.wo_lost_id = mpwl.id
                                AND sp.wo_lost_id IN (
                     SELECT mpwl.id as id
                    FROM mrp_production_workcenter_line mpwl
                    where mpwl.production_id =%s
                                 )
                GROUP BY mp.id, mp.name
                ) as mrp
                GROUP BY mrp.id
                ) as diamond ON(diamond.id = mrp.id)
                group by mrp.id, mrp.name,pp.coeff_24k
                having coalesce(sum(tab1.qty),0)
                +coalesce(sum(tab1.qty_24k),0)+ coalesce(sum(tab2.qty),0)
                +coalesce(sum(tab2.qty_24k),0)+ coalesce(sum(tab3.weight_ct),0)
                +coalesce(sum(tab3.weight_gr),0)+ coalesce(sum(tab4.weight_ct),0)
                +coalesce(sum(tab4.weight_gr),0)+ coalesce(sum(tab5.weight_gr),0)
                +coalesce(sum(tab6.weight_gr),0)<>0
            """%(mrp.id,mrp.id,mrp.id,mrp.id,mrp.id,mrp.id,mrp.id,mrp.id,mrp.id,mrp.id)

            cr.execute(sql)
            print sql
            result = cr.dictfetchall()


            for item in result:
                loss_percent=0
                weight_24k_used = 0
                weight_24k_return=0
                loss_weight_24 = 0
                net_weight =0
                loss_weight= item['metal_delivery'] - item['metal_return'] - (item['finish_return'] - item['finish_delivery'] - item['diamond_weight'])
                net_weight = float(item['finish_return'] - (item['finish_delivery'] +item['diamond_weight']) or 0)
                if net_weight!=0:
                    loss_percent =  (loss_weight/net_weight)*100
                if item['finish_delivery'] >0:
                    weight_24k_used = ((item['finish_delivery'] -item['diamond_weight']) *mrp.product_id.coeff_24k)  +item['total_metal24k_delivery']
                else:
                    weight_24k_used =  item['total_metal24k_delivery']

                if item['sub_total_24k_return']>0:
                    weight_24k_return= item['total_24k_return'] + item['sub_total_24k_return']
                else:
                    weight_24k_return= item['total_24k_return']

                if mrp.product_id.metal_class !='platinum':
		    #print 'casting_type: '+ str(mrp.product_id.casting_type)
                    loss_weight_24= loss_weight * item['coeff_24k']


                res = self.write(cr, uid, ids, {'metal_delivery':item['metal_delivery']
                                            ,'metal_return':item['metal_return']
                                            ,'diamond_weight': item['diamond_weight']
                                            ,'loss_weight':loss_weight
                                            ,'finished_weight':item['finish_return'] - item['finish_delivery']
                                            ,'loss_percent':loss_percent
                                            ,'metal_used': item['metal_delivery'] - item['metal_return']
                                            ,'metal_in_product':item['finish_return'] - (item['finish_delivery'] +item['diamond_weight'])
                                            ,'diamond_used':item['diamond_weight']
                                            , 'loss_weight_24k':loss_weight_24 }
                             , context=context)

        return True


    _columns = {
            'wo_id': fields.function(_get_mo, type='many2one', relation="mrp.workcenter", string='Workcenter', multi='mo'),
            'wo_view': fields.char('WorkCenter'),
            'state_view': fields.char('Work Order State'),
            'employee_id': fields.many2one('hr.employee','Worker'),
            'metal_delivery': fields.float('Total Metal Delivery'),
            'metal_return': fields.float('Total Metal Return'),
            'metal_used': fields.float('Metal Used Weight'),
            'metal_in_product': fields.float('Net Weight'),
            'finished_weight': fields.float('Finished Weight'),
            'diamond_used': fields.float('Quantity Diamonds ' ),
            'diamond_weight': fields.float('Diamond Weight'),
            'loss_weight': fields.float('Loss Weight'),
            'loss_weight_24k': fields.float('Loss Weight 24K'),
            'loss_percent': fields.float('Loss Percent'),
            'mo_date': fields.date('Manufacturing Date'),

                    }
    #Do not touch _name it must be same as _inherit
    #_name = 'mrp.production'
mrp_production()
