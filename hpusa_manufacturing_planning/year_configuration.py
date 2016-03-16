'''
Created on Aug 25, 2015

@author: Intern ERP Long
'''
from dateutil import relativedelta
import time
from datetime import datetime
#from datetime import timedelta
from openerp.osv import fields, osv
import locale
locale.setlocale(locale.LC_ALL,"")
import sys;
reload(sys);
sys.setdefaultencoding("utf8")

class year_configuration (osv.osv):
    _name  = 'year.configuration'
     
    _columns = {
            'name': fields.char('Name',size=64,required = True),
                                           
     }
year_configuration()