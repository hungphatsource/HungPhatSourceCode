import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class product_product(osv.osv):
    _inherit = "product.product" 
    def _get_percent_complete(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            sum_3d = 0.0
            sum_casting = 0.0
            sum_ass = 0.0
            sum_setting = 0.0
            if obj._3d_design_times:
                _ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('product_id', '=', obj.id), ('_3d_design_times', '=', obj._3d_design_times.id)])
                for _object in self.pool.get('hpusa.3d.report.line').browse(cr, uid, _ids):
                    sum_3d += _object.complete

            if obj.casting_times:
                _ids = self.pool.get('hpusa.casting.report.line').search(cr, uid, [('product_id', '=', obj.id), ('casting_times', '=', obj.casting_times.id)])
                for _object in self.pool.get('hpusa.casting.report.line').browse(cr, uid, _ids):
                    sum_casting += _object.complete

            if obj.ass_difficulty_level:
                _ids = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('product_id', '=', obj.id)]) 
                for _object in self.pool.get('hpusa.assembling.report.line').browse(cr, uid, _ids):
                    sum_ass += _object.complete

            if obj.setting_difficulty_level:
                _ids = self.pool.get('hpusa.setting.report.line').search(cr, uid, [('product_id', '=', obj.id)]) 
                for _object in self.pool.get('hpusa.setting.report.line').browse(cr, uid, _ids):
                    sum_setting += _object.complete

            res[obj.id] = {
                    '_3d_percent_complete': sum_3d,
                    'casting_percent_complete': sum_casting,
                    'ass_percent_complete': sum_ass,
                    'setting_percent_complete': sum_setting,
            }
        return res
    _columns = {
        #'_3d_percent_complete': fields.function(_get_percent_complete,type='float',string='percent_complete', multi="percent_complete"),
        #'casting_percent_complete': fields.function(_get_percent_complete,type='float',string='percent_complete', multi="percent_complete"),
        #'ass_percent_complete': fields.function(_get_percent_complete,type='float',string='percent_complete', multi="percent_complete"),
        #'setting_percent_complete': fields.function(_get_percent_complete,type='float',string='percent_complete', multi="percent_complete"),
        '_3d_difficulty_level': fields.many2one('hpusa3d.difficulty.level','3D Difficulty Level'),
        '_3d_design_times': fields.many2one('hpusa3d.times','3D Design Times'),
        'casting_times':  fields.many2one('hpusa.casting.times','Casting Times'),
        'casting_type': fields.selection([
             ('gold', 'Gold'),
             ('platinum', 'Platinum')
             ], 'Type',select=True),
        'ass_difficulty_level': fields.many2one('hpusa.ass.difficulty.level','Assembling Difficulty Level'),
        'setting_difficulty_level': fields.many2one('hpusa.setting.difficulty.level','Setting Difficulty Level'),
    }
product_product()  