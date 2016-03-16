from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):

    _name="stock.picking"
    _inherit=['stock.picking','mail.thread', 'ir.needaction_mixin']
    def default_update(self, cr, uid, ids, context=None):
        stock_picking = self.browse(cr,uid,ids[0],context=None)
        date = stock_picking.date
        sql ='''update stock_move set date='%s' where picking_id=%s '''%(date,ids[0])
        cr.execute(sql)
        cr.commit()
        
        return True
stock_picking()
