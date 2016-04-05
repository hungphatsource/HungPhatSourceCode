# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class sale_order(osv.osv):
    _inherit="sale.order"
    
    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        proc_obj = self.pool.get('procurement.order')
        for sale in self.browse(cr, uid, ids, context=context):
            for pick in sale.picking_ids:
                if pick.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel sales order!'),
                        _('You must first cancel all delivery order(s) attached to this sales order.'))
                if pick.state == 'cancel':
                    for mov in pick.move_lines:
                        proc_ids = proc_obj.search(cr, uid, [('move_id', '=', mov.id)])
                        if proc_ids:
                            for proc in proc_ids:
                                wf_service.trg_validate(uid, 'procurement.order', proc, 'button_check', cr)
            for inv in sale.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel this sales order!'),
                        _('First cancel all invoices attached to this sales order.'))
            for r in self.read(cr, uid, ids, ['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
            sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line],
                    {'state': 'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    
    def action_set_to_draft(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft','shipped':0, 'invoiced': 0, 'create_uid': False, 'validator': False})
        for sale in self.browse(cr, uid, ids, context=context):
            self.pool['sale.order.line'].write(cr, uid, [l.id for l in  sale.order_line], {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            wf_service.trg_delete(uid, 'sale.order', p_id, cr)
            wf_service.trg_create(uid, 'sale.order', p_id, cr)
        return True

    # Kim: eidt action view vs action_create_mo 
    def action_view_mo(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'hpusa_manufacturing', 'sale_open_mo')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        mo_ids = []
        for obj in self.browse(cr, uid, ids, context=context):
            mo_ids = self.pool.get('mrp.production').search(cr, uid, [('so_id','=',obj.id)])
        if len(mo_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, mo_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_manufacturing', 'hp_mrp_production_form_view')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = mo_ids and mo_ids[0] or False
        return result
    
    def action_create_mo(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        production_obj = self.pool.get('mrp.production')
        for obj in self.browse(cr, uid, ids):
            for line in obj.order_line:
                mo_ids = production_obj.search(cr, uid, [('so_id','=',obj.id),('product_id','=',line.product_id.id),('state','!=','cancel')])
                if len(mo_ids) == len(obj.order_line):
                    raise osv.except_osv(_('Error!'), _('There is exist Manufacturing Order for product %s!'%line.product_id.name))
                res = {}
                company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
                newdate = datetime.strptime(obj.date_order, '%Y-%m-%d') - relativedelta(days=line.product_id.produce_delay or 0.0)
                newdate = newdate - relativedelta(days=company.manufacturing_lead)
                if not mo_ids:
                    produce_id = production_obj.create(cr, uid, { 'origin': obj.name,'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty, 'product_uom': line.product_uom.id,
                        'so_id': obj.id,'so_line_id': line.id,'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,'bom_id': False,
                        'location_src_id': production_obj._src_id_default(cr, uid, []),'location_dest_id': production_obj._dest_id_default(cr, uid, []),
                        'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),'company_id': obj.company_id and obj.company_id.id or False})
                    bom_result = production_obj.action_compute(cr, uid,[produce_id], [])
                    wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
        return True
sale_order()