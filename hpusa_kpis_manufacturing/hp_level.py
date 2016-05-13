import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class hpusa3d_difficulty_level(osv.osv):
    _name = "hpusa3d.difficulty.level" 
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.config.3d', 'Parent'),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name'),
        'coefficient': fields.float('Coefficient'),
    }
hpusa3d_difficulty_level() 
class hpusa3d_times(osv.osv):
    _name = "hpusa3d.times" 
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.config.3d', 'Parent'),
        'sequence': fields.integer('Sequence'),
        'name': fields.integer('Name'),
        'coefficient': fields.float('Coefficient'),
    }
hpusa3d_times()  

class hpusa_casting_times(osv.osv):
    _name = "hpusa.casting.times" 
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.config.casting', 'Parent'),
        'sequence': fields.integer('Sequence'),
        'name': fields.integer('Name',required=True), 
        'coefficient_gold': fields.float('Coefficient gold'),
        'coefficient_pt': fields.float('Coefficient Platinum'),
    }
hpusa_casting_times() 

class hpusa_ass_difficulty_level(osv.osv):
    _name = "hpusa.ass.difficulty.level"
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.config.assembling', 'Parent'),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name'),
        'coefficient': fields.float('Coefficient'),
        'times': fields.integer('Times')
    }
hpusa_ass_difficulty_level() 

class hpusa_setting_difficulty_level(osv.osv):
    _name = "hpusa.setting.difficulty.level"
    _columns = {
        'parent_id': fields.many2one('hpusa.kpis.config.setting', 'Parent'),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name'),
        'coefficient': fields.float('Coefficient'),
        'description': fields.text('Description')
    }
hpusa_setting_difficulty_level()