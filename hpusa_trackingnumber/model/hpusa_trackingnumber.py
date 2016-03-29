'''
Created on Mar 28, 2016

@author: Intern ERP Long
'''
from osv import fields, osv
from tools.translate import _
import time
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw
from docutils.languages import de
from openerp import SUPERUSER_ID
from openerp.osv.fields import one2many
class hpusa_trackingnumber (osv.osv):
    _name = "hpusa.trackingnumber"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {'name':fields.char("Tracking Number" ,required=True),
                'delivery_method': fields.char("Delivery Method"),
                'shipment_weight': fields.float ("Shipment Weight"),
                'company': fields.many2one("res.company","Company"),     
                'shipping_cost':fields.float("Shipping Cost"),
                'date_of_tranfer':fields.date("Date of Tranfer"),
                'number_of_packages':fields.float("Number of Packages"),
                'create_date':fields.date("Creation Date"),
                'scheduled_date':fields.date("Scheduled Date"),
                'received_date':fields.date("Received Date"),
                'delivery_address':fields.char("Delivery Address"),
                'received_address':fields.char("Received Address"),
                'priority': fields.integer("Priority"),
                'source_doccument': fields.char("Source Doccument"),
                'shipping_product':fields.one2many('sale.order.track','shipping_id','SO Name')
                }
hpusa_trackingnumber()
class inherit_sale(osv.osv):
    _name = "sale.order.track"
    _columns = {'shipping_id':fields.many2one ("hpusa.trackingnumber" , 'Shipping'),
                'so_id':fields.many2one("sale.order","SO Name"),
                'customer_name':fields.related('so_id','partner_id', type ='many2one',relation='res.partner',string='Customer Name', readonly=True),
                'date_order': fields.related ('so_id', 'date_order' , type = 'date',string='Date Order' , readonly=True),
                'partner_shipping': fields.related('so_id','partner_shipping_id', type ='many2one',relation='res.partner',string='Delivery Address', readonly=True),
                }
    def onchange_data (self ,cr,uid, ids,so_id ,context = None):
        arr = self.pool.get('sale.order').browse(cr, uid,so_id,context= None)
        if arr:
            return {'value':{'customer_name':arr.partner_id.id ,'date_order':arr.date_order,'partner_shipping':arr.partner_shipping_id.id }}
  
        return {}
inherit_sale()
