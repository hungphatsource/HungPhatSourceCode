# Embedded file name: /home/tranhung/OpenERP/7.0/Project/GreenERP/openerp/openerp/addons-hp/green_erp_hp_mrp/mrp.py
import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp import netsvc
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {'bom_lines': fields.one2many('mrp.production.bom.line', 'production_id', 'Bom line', readonly=True, states={'draft': [('readonly', False)]})}

    def create(self, cr, uid, vals, context = None):
        if 'bom_id' in vals:
            bom = self.pool.get('mrp.bom').browse(cr, uid, vals['bom_id'])
            data = []
            for bom_line in bom.bom_lines:
                data.append((0, 0, {'product_id': bom_line.product_id.id or False,
                  'product_qty': bom_line.product_qty,
                  'product_uom': bom_line.product_uom.id or False}))

            vals.update({'bom_lines': data})
        new_id = super(mrp_production, self).create(cr, uid, vals, context)
        return new_id

    def action_update(self, cr, uid, ids, context = None):
        for production in self.browse(cr, uid, ids):
            data = []
            cr.execute('delete from mrp_production_bom_line where production_id = %s' % production.id)
            bom_id = production.bom_id
            if not bom_id:
                bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', production.product_id.id),
                 ('bom_id', '=', False),
                 '|',
                 ('date_start', '=', False),
                 ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                 '|',
                 ('date_stop', '=', False),
                 ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))])
                bom_id = self.pool.get('mrp.bom').browse(cr, uid, bom_ids[0])
            for bom_line in bom_id.bom_lines:
                data.append((0, 0, {'product_id': bom_line.product_id.id or False,
                  'product_qty': bom_line.product_qty * production.product_qty,
                  'product_uom': bom_line.product_uom.id or False}))

            self.write(cr, uid, ids, {'bom_lines': data}, context=context)

        return True


mrp_production()

class mrp_production_bom_line(osv.osv):
    _name = 'mrp.production.bom.line'
    _description = 'Production Bom Line'
    _columns = {'product_id': fields.many2one('product.product', 'Product', required=True),
     'product_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
     'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
     'production_id': fields.many2one('mrp.production', 'Production Order', select=True)}


mrp_production_bom_line()

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def make_mo(self, cr, uid, ids, context = None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService('workflow')
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            bom_id = procurement.bom_id.id
            vals = self._prepare_mo_vals(cr, uid, procurement, context=context)
            produce_id = production_obj.create(cr, uid, vals, context=context)
            production_obj.action_update(cr, uid, [produce_id])
            res[procurement.id] = produce_id
            self.write(cr, uid, [procurement.id], {'state': 'running',
             'production_id': produce_id})
            bom_result = production_obj.action_compute(cr, uid, [produce_id], properties=[ x.id for x in procurement.property_ids ])
            wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)

        self.production_order_create_note(cr, uid, ids, context=context)
        return res


procurement_order()
