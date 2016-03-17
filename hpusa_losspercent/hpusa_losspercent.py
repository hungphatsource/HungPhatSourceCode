'''
Created on Mar 17, 2016

@author: Intern ERP Long
'''
from dateutil import relativedelta
import time
from datetime import datetime
#from datetime import timedelta
from openerp.osv import fields, osv
import locale
from openerp.addons.pxgo_openoffice_reports import openoffice_report
#from winnt import NULL
#from pip._vendor.pkg_resources import require
#from openerp.netsvc import DEFAULT
#from pychart.line_style import default
#from decimal import Context
locale.setlocale(locale.LC_ALL,"")
import sys;
reload(sys);
sys.setdefaultencoding("utf8")
class hpusa_losspercent(osv.osv):
    _inherit = "mrp.workcenter"
    _columns = {'percent':fields.float("Loss Percent Limit" , required = True),
                
                }
    _defaults = {
                'percent' : 0.0
                }
hpusa_losspercent ()
    