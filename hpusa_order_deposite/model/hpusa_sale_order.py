'''
Created on Jan 30, 2016

@author: Thanh Thuan Lieu
'''
from dateutil import relativedelta
import time
from datetime import datetime
#from datetime import timedelta
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
class deposit_amount (osv.osv):
    _inherit = "sale.order"
     
    _columns = {
            'deposit_amount': fields.float('Deposit Amount'),
            
                 
     }
    _defaults={  
              'deposit_amount':0.0,
              
    } 
    def onchange_amount(self,cr,uid,ids,deposit, untax,context=None):
        val={}
        total =  untax - deposit
        val['amount_total'] = total
        self.write(cr, uid,ids, val, context=context)
        return {'value':val}
deposit_amount() 