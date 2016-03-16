import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp


class mrp_production_workcenter_line(osv.osv):
    _inherit = "account.invoice"
   
    def _paid_amount(self, cr, uid, ids, name, args, context=None):
 
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.amount_total - obj.residual or 0
            print 'Deposit: '+ str(obj.amount_total - obj.residual or 0)
        return result
   
   
    _columns = {
         'paid_amount': fields.function(_paid_amount,string='Paid', type="float",
            digits_compute= dp.get_precision('Account'), store=True)
         
         }