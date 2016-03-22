
from openerp.osv import fields, osv
import time
from datetime import datetime
from dateutil import relativedelta

class hpusa_vinvoice_number(osv.osv):
    
    _name="hpusa.vinvoice.number"
    _description="HP Invoice Number"
    
    _columns={
            'name':fields.char('Name'),
            'date_send': fields.date('Date Send'),
            'date_from': fields.date('Date From',required=True),
            'date_to': fields.date('Date To',required=True),
            'so_ids': fields.many2many('sale.order','vinvoice_sale_order_hpusa_invoice', 'vinvoice_wizard_hpusa_invoice_id', 'sale_order_id','Sale Orders'),
            'description':fields.text('Description'),
                              
              }
hpusa_vinvoice_number()
