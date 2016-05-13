import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp import netsvc
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
class hpusa_metal (osv.osv):
    _name = "hpusa.metal"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {'conff': fields.float("Confficent" , required=True), 
                }
    _rec_name = "conff"
hpusa_metal ()
    