'''
Created on Aug 25, 2015

@author: Intern ERP Long
'''
from dateutil import relativedelta
import time
from datetime import datetime
#from datetime import timedelta
from openerp.osv import fields, osv
from openerp.osv.fields import one2many, many2one
from email import _name
class hpusa_manufacturing_planning(osv.osv):
    _name  = 'hpusa.manufacturing.planning'
    
    _inherit = ['mail.thread', 'ir.needaction_mixin'] 
    
    def _get_qty(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for planning in self.browse(cursor, user, ids, context=context):
            lines= self.pool.get('hpusa.manufacturing.planning.line').search(cursor,user,[('planning_id','=',planning.id)],context=None)
            res[planning.id] = len(lines)
            
        return res
        
    _columns = {
            'name': fields.char('Name', required = True),
            'date_start': fields.date('Date Start','date',require = True),
            'date_End': fields.date('Date End','date',require = True),
            'month': fields.selection([('January' ,'January'),('February','February'),('March','March'),('April','April'),
                                       ('May','May'),('June','June'),('July','July'),('August','August'),
                                       ('September','September'),('October','October'),('November','November'),('December','December')],"Month" ,readonly=False),
            'year':fields.many2one('year.configuration', 'Year'),
            'mo_line_id':fields.one2many('hpusa.manufacturing.planning.line','planning_id','Manufacturing') ,
            'company_id': fields.many2one('res.company','Company'),
            'product_qty': fields.function(_get_qty,string='Quantity', type='float'),
            
     }
    _defaults = {
                'date_start': lambda *a: time.strftime('%Y-%m-01'),
                'date_End': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10], 
                 }

hpusa_manufacturing_planning()

class planning_line(osv.osv):
    _name="hpusa.manufacturing.planning.line"
    _columns = {
           
            'planning_id': fields.many2one('hpusa.manufacturing.planning', 'Planning'),
            'mo_id':fields.many2one('mrp.production','Manufacturing', required = True) ,
            'product_name': fields.related('mo_id','product_id', type ='many2one' ,relation='product.product',string='Product Name', readonly=True),
            'wo': fields.related('mo_id','wo_view', type ='char' ,string='Work Center',readonly=True),
            'work_state': fields.related('mo_id','state_view', type ='char',string='Work State', readonly=True),
            'mo_date': fields.related('mo_id','mo_date', type ='date',string='Manufacturing Date' , readonly=True),
            'finished_weight': fields.related('mo_id','finished_weight', type ='float',string='Finished Weight' , readonly=True),
            'loss_weight': fields.related('mo_id','loss_weight', type ='float',string='Loss Weight' , readonly=True),
            'loss_percent': fields.related('mo_id','loss_percent', type ='float',string='Loss Percent' , readonly=True),
            'employee_id': fields.related('mo_id','employee_id', type ='many2one' ,relation='hr.employee',string='Employee', readonly=True),
            
        
     }
    def onchange_data (self ,cr,uid, ids,mo_id ,context = None):
        arr = self.pool.get('mrp.production').browse(cr, uid,mo_id,context= None)
        if arr:
            return {
                    'value':
                    {'product_name':arr.product_id.id ,
                     'work_state':arr.state_view,
                     'mo_date':arr.mo_date, 
                     'wo': arr.wo_view,
                     'finished_weight':arr.finished_weight,
                     'loss_weight': arr.loss_weight,
                     'loss_percent': arr.loss_percent,
                      }}
  
        return {}
planning_line()  
