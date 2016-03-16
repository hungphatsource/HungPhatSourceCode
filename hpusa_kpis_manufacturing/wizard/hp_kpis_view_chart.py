from osv import fields, osv
from tools.translate import _
from dateutil import relativedelta
import time
from datetime import datetime
from datetime import timedelta
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw

class hp_kpis_view_chart_3d(osv.osv):
    _name = "hp.kpis.view.chart.3d"
    _columns = {
        'name': fields.char('Week/Month'),
        'quantity': fields.float('Quantity'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_3d()

class hp_kpis_view_chart_3d_productivity(osv.osv):
    _name = "hp.kpis.view.chart.3d.productivity"
    _columns = {
        'name': fields.char('Week/Month'),
        'type': fields.selection([
                    ('1', 'Design 1 time'),
                    ('2', 'Design 2 times'),
                    ('3', 'Design 3 times'),
                    ('4', 'Design >3 times'),
                    ], 'Type',select=True,),
        'quantity': fields.float('Quantity'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_3d_productivity()

class hp_kpis_view_chart_3d_compare(osv.osv):
    _name = "hp.kpis.view.chart.3d.compare"
    _columns = {
        'name': fields.char('Week/Month'),
        'employee_id': fields.many2one('hr.employee', 'Worker'),
        'quantity': fields.float('Quantity'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_3d_productivity()


class hp_kpis_view_chart_casting(osv.osv):
    _name = "hp.kpis.view.chart.casting"
    _columns = {
        'name': fields.char('Month/Week'),
        'quantity': fields.float('Quantity'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_casting()


class hp_kpis_view_chart_assembling(osv.osv):
    _name = "hp.kpis.view.chart.assembling"
    _columns = {
        'name': fields.char('Month/Week'),
        'quantity': fields.float('Quantity'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_assembling()

class hp_kpis_view_chart_assembling_compare(osv.osv):
    _name = "hp.kpis.view.chart.assembling.compare"
    _columns = {
        'name': fields.char('Week/Month'),
        'employee_id': fields.many2one('hr.employee', 'Worker'),
        'quantity': fields.float('Quantity'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_assembling_compare()

class hp_kpis_view_chart_setting(osv.osv):
    _name = "hp.kpis.view.chart.setting"
    _columns = {
        'name': fields.char('Month/Week'),
        'quantity': fields.float('Quantity'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_setting()

class hp_kpis_view_chart_setting_compare(osv.osv):
    _name = "hp.kpis.view.chart.setting.compare"
    _columns = {
        'name': fields.char('Month/Week'),
        'quantity': fields.float('Quantity'),
        'employee_id': fields.many2one('hr.employee', 'Worker'),
        'point': fields.float('Point'),
     }  
hp_kpis_view_chart_setting_compare()

