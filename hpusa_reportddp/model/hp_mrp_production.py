import tools
from osv import fields, osv
from openerp import SUPERUSER_ID

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    
    _columns = {
          'description': fields.text('Notes'),
    }