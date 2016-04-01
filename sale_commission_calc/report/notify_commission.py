# -*- coding: utf-8 -*-
##############################################################################
##############################################################################

import time
from openerp.report import report_sxw

class notify_commission(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(notify_commission, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
    def get_order(self, invoice):
        sql = ''' SELECT date_order, name FROM sale_order_invoice_rel rel 
                  LEFT JOIN sale_order ord ON(ord.id = rel.order_id)
                  WHERE rel.invoice_id = %s
                  '''%(invoice)
        self.cr.execute(sql)
        result = self.cr.dictfetchall()
        if result:
            return result[0]
        
report_sxw.report_sxw('report.hpsua_report_commission', 'commission.worksheet', 'addons/sale_commission_calc/report/notify_commission.rml', parser=notify_commission, header="internal landscape")
