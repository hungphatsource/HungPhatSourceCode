import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class product_product(osv.osv):
    _inherit = "product.product" 
    _columns = {
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