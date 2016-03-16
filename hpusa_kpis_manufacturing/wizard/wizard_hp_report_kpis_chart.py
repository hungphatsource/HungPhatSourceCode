from osv import fields, osv
from tools.translate import _
from dateutil.relativedelta import relativedelta
import time
from datetime import datetime
from datetime import timedelta
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw

class wizard_hp_report_chart_kpis(osv.osv_memory):
    _name = "wizard.hp.report.chart.kpis"
    _columns = {
        'type': fields.selection([
                    ('3d', '3D Design'),
                    ('casting', 'Casting'),
                    ('assembling', 'Assembling'),
                    ('setting', 'Setting'),
                    ], 'Report Type',select=True,required=True),
        'option': fields.selection([
                    ('month', 'Month Report'),
                    ('year', 'Year Report'),
                    ], 'Option',select=True),
        'month': fields.many2one('account.period', 'Month'),
        'month_from': fields.many2one('account.period', 'Month From'),
        'month_to': fields.many2one('account.period', 'Month To'),
     }
    _defaults={
              'option': 'month'
    }

wizard_hp_report_chart_kpis()

class wizard_hp_report_chart_kpis_3d(osv.osv_memory):
    _name = "wizard.hp.report.chart.kpis.3d"
    _table = "wizard_hp_report_chart_kpis"
    _inherit = "wizard.hp.report.chart.kpis" 
    _columns = {
        'type_report': fields.selection([
                    ('synthetic', 'Synthetic chart'),
                    ('productivity', 'Productivity chart'),
                    ('productivity_worker', 'Productivity chart of worker'),
                    ('compare', 'Comparing synthesis workers'),
                    ], 'Chart Type',select=True,required=True),
        'employee_id': fields.many2one('hr.employee', 'Worker'),
    }
    def action_view_chart(self, cr, uid, ids, context):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        obj = self.browse(cr, uid, ids[0], context)
        if obj.type_report == 'synthetic':
            _3d_ids = self.pool.get('hp.kpis.view.chart.3d').search(cr, uid, [])
            if(_3d_ids):
                self.pool.get('hp.kpis.view.chart.3d').unlink(cr, uid, _3d_ids)
            if obj.option == 'month':
                date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
                for i in range(1, 5):
                    #tinh ngay cua tung tuan
                    if(i == 1):
                        date_from =  date_to    
                    else:
                        date_from =  date_to + relativedelta(days=1)
                    date_to = date_from + relativedelta(days=6)
                    #get report 3d line
                    _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                    point = 0
                    qty = 0
                    for _3d_report_id in _3d_report_ids:
                        line = self.pool.get('hpusa.3d.report.line').browse(cr, uid, _3d_report_id)
                        point += line.point
                        qty += 1 * line.complete
                    self.pool.get('hp.kpis.view.chart.3d').create(cr, uid, {'name': 'Week '+str(i),'point': point, 'quantity': qty})
                    
            else:
                #get month list
                month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
                for i in month_ids:
                    # month
                    month = self.pool.get('account.period').browse(cr, uid, i, context)
                    if month.date_start != month.date_stop:
                        #get report 3d line
                        _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                        point = 0
                        qty = 0
                        for _3d_report_id in _3d_report_ids:
                            line = self.pool.get('hpusa.3d.report.line').browse(cr, uid, _3d_report_id)
                            point += line.point
                            qty += 1 * line.complete
                        self.pool.get('hp.kpis.view.chart.3d').create(cr, uid, {'name': month.name,'point': point, 'quantity': qty})    
            #open action
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_3d_graph')
            
        elif obj.type_report == 'productivity' or obj.type_report == 'productivity_worker':
            _3d_ids = self.pool.get('hp.kpis.view.chart.3d.productivity').search(cr, uid, [])
            if(_3d_ids):
                self.pool.get('hp.kpis.view.chart.3d.productivity').unlink(cr, uid, _3d_ids)
            if obj.option == 'month':
                date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
                for i in range(1, 5):
                    #khoi tao cot cho moi tuan
                    self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': 'Week '+str(i), 'type':'1', 'point': 0, 'quantity': 0})
                    self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': 'Week '+str(i), 'type':'2', 'point': 0, 'quantity': 0})
                    self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': 'Week '+str(i), 'type':'3', 'point': 0, 'quantity': 0})
                    self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': 'Week '+str(i), 'type':'4', 'point': 0, 'quantity': 0})
                    #tinh ngay cua tung tuan
                    if i == 1:
                        date_from =  date_to  
                        date_to = date_from + relativedelta(days=6)
                    else:
                        date_from =  date_to + relativedelta(days=1)
                    if i == 4:
                        date_to = obj.month.date_stop
                    elif i !=1 :
                        date_to = date_from + relativedelta(days=7)
                    #get report 3d line
                    if(not obj.employee_id):
                        _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                    else:
                        _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.designer_id','=',obj.employee_id.id),('parent_id.state','=','confirmed')])
                    for _3d_report_id in _3d_report_ids: 
                        _3d_report = self.pool.get('hpusa.3d.report.line').browse(cr, uid, _3d_report_id)
                        if _3d_report.product_id._3d_design_times:
                            times = _3d_report.product_id._3d_design_times.name
                            if times > 3:
                                self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': 'Week '+str(i), 'type':'4', 'point': _3d_report.point, 'quantity': 1 * _3d_report.complete})
                            else:
                                self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': 'Week '+str(i), 'type': str(times), 'point': _3d_report.point, 'quantity': 1 * _3d_report.complete})
            else:
                month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
                for i in month_ids:
                    # month
                    month = self.pool.get('account.period').browse(cr, uid, i, context)
                    if month.date_start != month.date_stop:
                        self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': month.name, 'type':'1', 'point': 0, 'quantity': 0})
                        self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': month.name, 'type':'2', 'point': 0, 'quantity': 0})
                        self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': month.name, 'type':'3', 'point': 0, 'quantity': 0})
                        self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': month.name, 'type':'4', 'point': 0, 'quantity': 0})
                        #get report 3d line
                        _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                        for _3d_report_id in _3d_report_ids: 
                            _3d_report = self.pool.get('hpusa.3d.report.line').browse(cr, uid, _3d_report_id)
                            if _3d_report.product_id._3d_design_times:
                                times = _3d_report.product_id._3d_design_times.name
                                if times > 3:
                                    self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': month.name, 'type':'4', 'point': _3d_report.point, 'quantity': 1 * _3d_report.complete})
                                else:
                                    self.pool.get('hp.kpis.view.chart.3d.productivity').create(cr, uid, {'name': month.name, 'type': str(times), 'point': _3d_report.point, 'quantity': 1 * _3d_report.complete})        
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_3d_productivity_graph')
        
        elif obj.type_report == 'compare':
            _3d_ids = self.pool.get('hp.kpis.view.chart.3d.compare').search(cr, uid, [])
            if(_3d_ids):
                self.pool.get('hp.kpis.view.chart.3d.compare').unlink(cr, uid, _3d_ids)
            if obj.option == 'month':
                date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
                for i in range(1, 5):
                    #tinh ngay cua tung tuan
                    if i == 1:
                        date_from =  date_to  
                        date_to = date_from + relativedelta(days=6)
                    else:
                        date_from =  date_to + relativedelta(days=1)
                    if i == 4:
                        date_to = obj.month.date_stop
                    elif i !=1 :
                        date_to = date_from + relativedelta(days=7)
                    #get report 3d line
                    _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                    for _3d_report_id in _3d_report_ids:
                        _3d_report = self.pool.get('hpusa.3d.report.line').browse(cr, uid, _3d_report_id)
                        self.pool.get('hp.kpis.view.chart.3d.compare').create(cr, uid, {'name': 'Week '+str(i),'employee_id':_3d_report.parent_id.designer_id.id,'point': _3d_report.point, 'quantity': 1 * _3d_report.complete})
                    
            else:
                #get month list
                month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
                for i in month_ids:
                    # month
                    month = self.pool.get('account.period').browse(cr, uid, i, context)
                    if month.date_start != month.date_stop:
                        #get report 3d line
                        _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                        for _3d_report_id in _3d_report_ids:
                            _3d_report = self.pool.get('hpusa.3d.report.line').browse(cr, uid, _3d_report_id)
                            self.pool.get('hp.kpis.view.chart.3d.compare').create(cr, uid, {'name': month.name,'employee_id':_3d_report.parent_id.designer_id.id,'point': _3d_report.point, 'quantity': 1 * _3d_report.complete})    
            #open action
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_3d_compare_graph')
                
        id = res and res[1] or False  
        result = act_obj.read(cr, uid, [id], context=context)[0]        
        result['target'] = 'current' 
        return result
    
wizard_hp_report_chart_kpis_3d() 

class wizard_hp_report_chart_kpis_casting(osv.osv_memory):
    _name = "wizard.hp.report.chart.kpis.casting"
    _table = "wizard_hp_report_chart_kpis"
    _inherit = "wizard.hp.report.chart.kpis" 
    
    def action_view_chart(self, cr, uid, ids, context):
        obj = self.browse(cr, uid, ids[0], context)
        _casting_ids = self.pool.get('hp.kpis.view.chart.casting').search(cr, uid, [])
        if(_casting_ids):
            self.pool.get('hp.kpis.view.chart.casting').unlink(cr, uid, _casting_ids)
        if(obj.option == 'month'):
            date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
            for i in range(1, 5):
                #tinh ngay cua tung tuan
                if(i == 1):
                    date_from =  date_to    
                else:
                    date_from =  date_to + relativedelta(days=1)
                date_to = date_from + relativedelta(days=6)
                print date_from, date_to
                #get report 3d line
                _casting_report_ids = self.pool.get('hpusa.casting.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                point = 0
                qty = 0
                for _casting_report_id in _casting_report_ids:
                    line =  self.pool.get('hpusa.casting.report.line').browse(cr, uid, _casting_report_id)
                    point += line.point
                    qty += line.complete
                self.pool.get('hp.kpis.view.chart.casting').create(cr, uid, {'name': 'Week '+str(i),'point': point, 'quantity': qty})
        else:
            #get month list
            month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
            for i in month_ids:
                # month
                month = self.pool.get('account.period').browse(cr, uid, i, context)
                if month.date_start != month.date_stop:
                    #get report 3d line
                    _casting_report_ids = self.pool.get('hpusa.casting.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                    point = 0
                    qty = 0
                    for _casting_report_id in _casting_report_ids:
                        line =  self.pool.get('hpusa.casting.report.line').browse(cr, uid, _casting_report_id)
                        point += line.point
                        qty += line.complete
                    self.pool.get('hp.kpis.view.chart.casting').create(cr, uid, {'name': month.name,'point': point, 'quantity': qty})
                    
        #open action
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        
        res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_casting_graph')
        id = res and res[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]        
        result['target'] = 'current' 
        return result
    
wizard_hp_report_chart_kpis_casting()   

class wizard_hp_report_chart_kpis_assembling(osv.osv_memory):
    _name = "wizard.hp.report.chart.kpis.assembling"
    _table = "wizard_hp_report_chart_kpis"
    _inherit = "wizard.hp.report.chart.kpis" 
    _columns = {
        'type_report': fields.selection([
                    ('synthetic', 'Synthetic chart'),
                    ('compare', 'Comparing synthesis workers'),
                    ], 'Chart Type',select=True,required=True),
    }
    def action_view_chart(self, cr, uid, ids, context):
        obj = self.browse(cr, uid, ids[0], context)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if(obj.type_report == 'synthetic'):
            _assembling_ids = self.pool.get('hp.kpis.view.chart.assembling').search(cr, uid, [])
            if(_assembling_ids):
                self.pool.get('hp.kpis.view.chart.assembling').unlink(cr, uid, _assembling_ids)
            if(obj.option == 'month'):
                date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
                for i in range(1, 5):
                    #tinh ngay cua tung tuan
                    if i == 1:
                        date_from =  date_to  
                        date_to = date_from + relativedelta(days=6)
                    else:
                        date_from =  date_to + relativedelta(days=1)
                    if i == 4:
                        date_to = obj.month.date_stop
                    elif i !=1 :
                        date_to = date_from + relativedelta(days=7)
                    #get report 3d line
                    _assembling_report_ids = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                    point = 0
                    qty = 0
                    for _assembling_report_id in _assembling_report_ids:
                        line =  self.pool.get('hpusa.assembling.report.line').browse(cr, uid, _assembling_report_id)
                        point += line.point
                        qty += 1 * line.complete
                    self.pool.get('hp.kpis.view.chart.assembling').create(cr, uid, {'name': 'Week '+str(i),'point': point, 'quantity': qty})
            else:
                #get month list
                month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
                for i in month_ids:
                    # month
                    month = self.pool.get('account.period').browse(cr, uid, i, context)
                    if month.date_start != month.date_stop:
                        #get report 3d line
                        _assembling_report_ids = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                        point = 0
                        qty = 0
                        for _assembling_report_id in _assembling_report_ids:
                            line =  self.pool.get('hpusa.assembling.report.line').browse(cr, uid, _assembling_report_id)
                            point += line.point
                            qty += 1 * line.complete
                        self.pool.get('hp.kpis.view.chart.assembling').create(cr, uid, {'name': month.name,'point': point, 'quantity': qty})
            #open action
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_assembling_graph')
            
        elif obj.type_report == 'compare':
            _assembling_ids = self.pool.get('hp.kpis.view.chart.assembling.compare').search(cr, uid, [])
            if(_assembling_ids):
                self.pool.get('hp.kpis.view.chart.assembling.compare').unlink(cr, uid, _assembling_ids)
            if obj.option == 'month':
                date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
                for i in range(1, 5):
                    #tinh ngay cua tung tuan
                    if i == 1:
                        date_from =  date_to  
                        date_to = date_from + relativedelta(days=6)
                    else:
                        date_from =  date_to + relativedelta(days=1)
                    if i == 4:
                        date_to = obj.month.date_stop
                    elif i !=1 :
                        date_to = date_from + relativedelta(days=7)
                    #get report 3d line
                    _assembling_report_ids = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                    for _assembling_report_id in _assembling_report_ids:
                        _assembling_report = self.pool.get('hpusa.assembling.report.line').browse(cr, uid, _assembling_report_id)
                        self.pool.get('hp.kpis.view.chart.assembling.compare').create(cr, uid, {'name': 'Week '+str(i),'employee_id':_assembling_report.worker.id,'point': _assembling_report.point, 'quantity': 1 * _assembling_report.complete})
                    
            else:
                #get month list
                month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
                for i in month_ids:
                    # month
                    month = self.pool.get('account.period').browse(cr, uid, i, context)
                    if month.date_start != month.date_stop:
                        #get report 3d line
                        _assembling_report_ids = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                        for _assembling_report_id in _assembling_report_ids:
                            _assembling_report = self.pool.get('hpusa.assembling.report.line').browse(cr, uid, _assembling_report_id)
                            self.pool.get('hp.kpis.view.chart.assembling.compare').create(cr, uid, {'name': month.name,'employee_id':_assembling_report.worker.id,'point': _assembling_report.point, 'quantity': 1 * _assembling_report.complete})    
            #open action
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_assembling_compare_graph')
            
        id = res and res[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]        
        result['target'] = 'current' 
        return result
    
wizard_hp_report_chart_kpis_assembling() 

class wizard_hp_report_chart_kpis_setting(osv.osv_memory):
    _name = "wizard.hp.report.chart.kpis.setting"
    _table = "wizard_hp_report_chart_kpis"
    _inherit = "wizard.hp.report.chart.kpis"
    _columns = {
        'type_report': fields.selection([
                    ('synthetic', 'Synthetic chart'),
                    ('compare', 'Comparing synthesis workers'),
                    ], 'Chart Type',select=True,required=True),
    }     
    def action_view_chart(self, cr, uid, ids, context):
        obj = self.browse(cr, uid, ids[0], context)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if(obj.type_report == 'synthetic'):
            _setting_ids = self.pool.get('hp.kpis.view.chart.setting').search(cr, uid, [])
            if(_setting_ids):
                self.pool.get('hp.kpis.view.chart.setting').unlink(cr, uid, _setting_ids)
            if(obj.option == 'month'):
                date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
                for i in range(1, 5):
                    #tinh ngay cua tung tuan
                    if i == 1:
                        date_from =  date_to  
                        date_to = date_from + relativedelta(days=6)
                    else:
                        date_from =  date_to + relativedelta(days=1)
                    if i == 4:
                        date_to = obj.month.date_stop
                    elif i !=1 :
                        date_to = date_from + relativedelta(days=7)
                    #get report 3d line
                    _setting_report_ids = self.pool.get('hpusa.setting.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                    point = 0
                    qty = 0
                    for _setting_report_id in _setting_report_ids:
                        line = self.pool.get('hpusa.setting.report.line').browse(cr, uid, _setting_report_id)
                        point += line.point
                        qty += 1 * line.complete
                    self.pool.get('hp.kpis.view.chart.setting').create(cr, uid, {'name': 'Week '+str(i),'point': point, 'quantity': qty})
            else:
                #get month list
                month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
                for i in month_ids:
                    # month
                    month = self.pool.get('account.period').browse(cr, uid, i, context)
                    if month.date_start != month.date_stop:
                        #get report 3d line
                        _setting_report_ids = self.pool.get('hpusa.setting.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                        point = 0
                        qty = 0
                        for _setting_report_id in _setting_report_ids:
                            line = self.pool.get('hpusa.setting.report.line').browse(cr, uid, _setting_report_id)
                            point += line.point
                            qty += 1 * line.complete
                        self.pool.get('hp.kpis.view.chart.setting').create(cr, uid, {'name': month.name,'point': point, 'quantity': qty})
                        
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_setting_graph')
        else:
            _setting_ids = self.pool.get('hp.kpis.view.chart.setting.compare').search(cr, uid, [])
            if(_setting_ids):
                self.pool.get('hp.kpis.view.chart.setting.compare').unlink(cr, uid, _setting_ids)
            if(obj.option == 'month'):
                date_to = datetime.strptime(obj.month.date_start, '%Y-%m-%d')
                for i in range(1, 5):
                    #tinh ngay cua tung tuan
                    if i == 1:
                        date_from =  date_to  
                        date_to = date_from + relativedelta(days=6)
                    else:
                        date_from =  date_to + relativedelta(days=1)
                    if i == 4:
                        date_to = obj.month.date_stop
                    elif i !=1 :
                        date_to = date_from + relativedelta(days=7)
                    #get report 3d line
                    _setting_report_ids = self.pool.get('hpusa.setting.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
                    for _setting_report_id in _setting_report_ids:
                        setting = self.pool.get('hpusa.setting.report.line').browse(cr, uid, _setting_report_id)
                        self.pool.get('hp.kpis.view.chart.setting.compare').create(cr, uid, {'name': 'Week '+str(i),'point': setting.point, 'quantity': 1 * setting.complete,'employee_id': setting.worker.id})
            else:
                #get month list
                month_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=',obj.month_from.date_start),('date_stop','<=',obj.month_to.date_stop)])
                for i in month_ids:
                    # month
                    month = self.pool.get('account.period').browse(cr, uid, i, context)
                    if month.date_start != month.date_stop:
                        #get report 3d line
                        _setting_report_ids = self.pool.get('hpusa.setting.report.line').search(cr, uid, [('parent_id.report_date','>=',month.date_start),('parent_id.report_date','<=',month.date_stop),('parent_id.state','=','confirmed')])
                        for _setting_report_id in _setting_report_ids:
                            setting = self.pool.get('hpusa.setting.report.line').browse(cr, uid, _setting_report_id)
                            self.pool.get('hp.kpis.view.chart.setting.compare').create(cr, uid, {'name': month.name,'point': setting.point, 'quantity': 1 * setting.complete, 'employee_id': setting.worker.id})
            res = mod_obj.get_object_reference(cr, uid, 'hpusa_kpis_manufacturing', 'action_hp_kpis_view_chart_setting_compare_graph')
        id = res and res[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]        
        result['target'] = 'current' 
        return result
    
wizard_hp_report_chart_kpis_setting()  



