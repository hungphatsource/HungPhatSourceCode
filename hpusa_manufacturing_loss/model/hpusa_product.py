
from osv import fields, osv
from tools.translate import _
from dateutil import relativedelta 
import time
from datetime import datetime
from datetime import timedelta
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw
import this

class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
            'metal_class': fields.selection([('gold','Gold'),('platinum','Platinum'),('paladium','Paladium')],'Metal Class'),
            'sub_class': fields.selection([('24k','24K'),('18k','18k'),('14k','14K'),('10k','10K')],'Sub Class'),
        
    }
    
    _defaults ={
              'metal_class':'gold',
              }
    def onchange_sub_class(self,cr,uid,ids,sub_class,context):
        cofficent = 0
        v={}
        if sub_class=="24k":
            cofficent =1
        elif sub_class=="18k":
            cofficent =0.75
        elif sub_class=="14k":
            cofficent =0.583
        elif sub_class=="10k":
            cofficent =0.4167
                    
        v['coeff_24k']=cofficent
        
        return {'value': v }
        
        
    
product_product()    