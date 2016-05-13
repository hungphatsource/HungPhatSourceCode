# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class sale_reutrn(osv.osv):
    _name = "sale.return"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns={
           'name': fields.char('Order Reference', size=64, required=True,
                               readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True),
            'state': fields.selection([
            ('draft', 'New'),
            ('cancel', 'Cancelled'),
            ('progress', 'Sales Return'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
              }
sale_reutrn()