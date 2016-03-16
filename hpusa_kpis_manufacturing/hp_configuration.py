import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta 

class hpusa_kpis_config(osv.osv):
    _name = "hpusa.kpis.config"
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Name',required=True),
        'manager': fields.many2one('hr.employee', 'Manager',required=True),
        'user_id': fields.many2one('res.users','User Create',required=True), 
        'hp_create_date': fields.date('Create Date', required=True),
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'company_id': fields.many2one('res.company','Company',required=True),
        'type': fields.selection([
                            ('3d', '3D Design'),
                            ('casting', 'Casting'),
                            ('assembling', 'Assembling'),
                            ('setting', 'Setting'),
                            ], 'Type',select=True, track_visibility='onchange'),
        'state': fields.selection([
            ('open', 'Open'),
            ('close', 'Close'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange',
        ),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        'user_id': lambda s, c, uid, ctx: uid,
        'state': 'open',
        'hp_create_date': lambda *a: time.strftime('%Y-%m-%d'),
        'start_date':  lambda *a: time.strftime('%Y-%m-01'),
        'end_date': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }  
    
    def action_close(self, cr, uid, ids, context=None):
        if not ids:
            return
        self.write(cr, uid, ids, {'state':'close'}, context)
        
    def action_open(self, cr, uid, ids, context=None):
        if not ids:
            return
        self.write(cr, uid, ids, {'state':'open'}, context)
        
hpusa_kpis_config()
    
class hpusa_kpis_config_3d(osv.osv):
    _name = "hpusa.kpis.config.3d"
    _table = "hpusa_kpis_config"
    _inherit = "hpusa.kpis.config" 
    _columns = {
        'standard_point': fields.float('Standard Point', required=True),
        'line_id_level': fields.one2many('hpusa3d.difficulty.level', 'parent_id','Lines Level'),
        'line_id_times': fields.one2many('hpusa3d.times', 'parent_id','Lines Times'),
    }
    _defaults = {
        'type': '3d'
    }  
    
hpusa_kpis_config_3d()  


class hpusa_kpis_config_casting(osv.osv):
    _name = "hpusa.kpis.config.casting" 
    _table = "hpusa_kpis_config"
    _inherit = "hpusa.kpis.config" 
    _columns = { 
        'standard_date_gold': fields.float('Standard date gold', required=True),
        'standard_date_platinum': fields.float('Standard date platinum', required=True),
        'line_ids': fields.one2many('hpusa.casting.times', 'parent_id','Lines'),
    }
    _defaults = {
        'type': 'casting'
    }  
hpusa_kpis_config_casting()  

class hpusa_kpis_config_assembling(osv.osv):
    _name = "hpusa.kpis.config.assembling" 
    _table = "hpusa_kpis_config"
    _inherit = "hpusa.kpis.config" 
    _columns = {
        'standard_date': fields.float('Standard date', required=True),
        'line_ids': fields.one2many('hpusa.ass.difficulty.level', 'parent_id','Lines'),
    }    
    _defaults = {
        'type': 'assembling'
    }  
hpusa_kpis_config_assembling()  


class hpusa_kpis_config_setting(osv.osv):
    _name = "hpusa.kpis.config.setting" 
    _table = "hpusa_kpis_config"
    _inherit = "hpusa.kpis.config" 
    _columns = {
        'standard_point_date': fields.float('Standard point date', required=True),
        'line_ids': fields.one2many('hpusa.setting.difficulty.level', 'parent_id','Lines'),
    } 
    _defaults = {
        'type': 'setting'
    }  
hpusa_kpis_config_setting()  
