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

class hpusa_kpis_target(osv.osv):
    _name = "hpusa.kpis.target" 
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Name', required=True),
        'hp_create_date': fields.date('Create Date', required=True),
        'user_id': fields.many2one('res.users','User Create',required=True), 
        'company_id': fields.many2one('res.company','Company',required=True),
        'type': fields.selection([
                            ('3d', '3D Design'),
                            ('casting', 'Casting'),
                            ('assembling', 'Assembling'),
                            ('setting', 'Setting'),
                            ], 'Type',select=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        'user_id': lambda s, c, uid, ctx: uid,
        'hp_create_date': lambda *a: time.strftime('%Y-%m-%d'),
    } 
hpusa_kpis_target()

class hpusa_kpis_target_3d(osv.osv):
    _name = "hpusa.kpis.target.3d" 
    _table = "hpusa_kpis_target"
    _inherit = "hpusa.kpis.target" 
    _columns = {
        'line_ids': fields.one2many('hpusa.kpis.target.3d.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': '3d'
    }
hpusa_kpis_target_3d()

class hpusa_kpis_target_3d_line(osv.osv):
    _name = "hpusa.kpis.target.3d.line" 
    def _get_coefficient(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
                res[obj.id] = obj.level.coefficient * obj.target;
        return res
    
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.target.3d', 'Parent'),
        'sequence': fields.integer('Sequence', required=True),
        'level': fields.many2one('hpusa3d.difficulty.level','Level',required=True), 
        'target': fields.float('Target/day', required=True),
        'coefficient_day': fields.function(_get_coefficient,type='float',string='Coefficient/day', track_visibility='onchange'),
    }
hpusa_kpis_target_3d_line()

class hpusa_kpis_target_casting(osv.osv):
    _name = "hpusa.kpis.target.casting" 
    _table = "hpusa_kpis_target"
    _inherit = "hpusa.kpis.target" 
    _columns = {
        'line_ids': fields.one2many('hpusa.kpis.target.casting.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': 'casting'
    }
hpusa_kpis_target_casting()

class hpusa_kpis_target_casting_line(osv.osv):
    _name = "hpusa.kpis.target.casting.line" 
    def _get_total(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
                res[obj.id] = obj.target * obj.day_month;
        return res
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.target.casting', 'Parent'),
        'sequence': fields.integer('Sequence', required=True),
        'casting_type': fields.selection([
             ('gold', 'Gold'),
             ('platinum', 'Platinum')
             ], 'Type',select=True),
        'target': fields.float('Target/day', required=True),
        'day_month': fields.integer('Days/month', required=True),
        'total': fields.function(_get_total,type='float',string='Total/month', track_visibility='onchange'),
        
    }
hpusa_kpis_target_casting_line()

class hpusa_kpis_target_assembling(osv.osv):
    _name = "hpusa.kpis.target.assembling" 
    _table = "hpusa_kpis_target"
    _inherit = "hpusa.kpis.target" 
    _columns = {
        'line_ids': fields.one2many('hpusa.kpis.target.assembling.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': 'assembling'
    }
hpusa_kpis_target_assembling()


class hpusa_kpis_target_assembling_line(osv.osv):
    _name = "hpusa.kpis.target.assembling.line" 
    def _get_total(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
                res[obj.id] = obj.target * obj.day_month;
        return res
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.target.assembling', 'Parent'),
        'sequence': fields.integer('Sequence', required=True),
        'level': fields.many2one('hpusa.ass.difficulty.level','Level',required=True), 
        'target': fields.float('Target/day', required=True),
        'day_month': fields.integer('Days/month', required=True),
        'total': fields.function(_get_total,type='float',string='Total/month', track_visibility='onchange'),
        
    }
hpusa_kpis_target_casting_line()

class hpusa_kpis_target_setting(osv.osv):
    _name = "hpusa.kpis.target.setting" 
    _table = "hpusa_kpis_target"
    _inherit = "hpusa.kpis.target" 
    _columns = {
        'line_ids': fields.one2many('hpusa.kpis.target.setting.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': 'setting'
    }
hpusa_kpis_target_assembling()

class hpusa_kpis_target_setting_line(osv.osv):
    _name = "hpusa.kpis.target.setting.line" 
    def _get_total(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
                res[obj.id] = obj.target * obj.day_month;
        return res
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.target.setting', 'Parent'),
        'sequence': fields.integer('Sequence', required=True),
        'level': fields.many2one('hpusa.setting.difficulty.level','Level',required=True), 
        'target': fields.float('Target/day', required=True),
        'day_month': fields.integer('Days/month', required=True),
        'total': fields.function(_get_total,type='float',string='Total/month', track_visibility='onchange'),
        
    }
hpusa_kpis_target_casting_line()

