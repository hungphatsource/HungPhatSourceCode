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
class hpusa_3d_design_planning(osv.osv):
    _name  = 'hpusa.3ddesign.planning'
    
    _description=''' 3D Design Planning '''
    
    _inherit = ['mail.thread', 'ir.needaction_mixin'] 
      
    _columns = {
            'name': fields.char('Name', required = True),
            'date_start': fields.date('Date Start','date',require = True),
            'date_end': fields.date('Date End','date',require = True),
            'month': fields.selection([('January' ,'January'),('February','February'),('March','March'),('April','April'),
                                       ('May','May'),('June','June'),('July','July'),('August','August'),
                                       ('September','September'),('October','October'),('November','November'),('December','December')],"Month" ,readonly=False),
            'year':fields.many2one('year.configuration', 'Year'),
            'design_line_id':fields.one2many('hpusa.3ddesign.planning.line','planning_id','Design') ,
            'company_id': fields.many2one('res.company','Company'),
            
            
     }
    _defaults = {
                'date_start': lambda *a: time.strftime('%Y-%m-01'),
                'date_end': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10], 
                 }

hpusa_3d_design_planning()

class design_planning_line(osv.osv):
    _name="hpusa.3ddesign.planning.line"
    _columns = {
           
            'planning_id': fields.many2one('hpusa.3ddesign.planning', 'Planning'),
            'product_id':fields.many2one('product.product','Product', required = True),
            'dificultive_level': fields.related('product_id','_3d_difficulty_level', type ='many2one' ,relation='hpusa3d.difficulty.level',string='Dificulty Level' , readonly=True),
            'date': fields.date('Date Design'),
            'qty': fields.float('Quantity'),
            'employee_id': fields.many2one('hr.employee','Designer'),
        
     }
    _defaults = {
                'qty': 1,
                
                 }
   
design_planning_line()  
