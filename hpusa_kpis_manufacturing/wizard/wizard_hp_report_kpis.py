from osv import fields, osv
from tools.translate import _
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
import time
from datetime import date 
from datetime import datetime
from datetime import timedelta
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw

class wizard_hp_report_kpis(osv.osv_memory):
    _name = "wizard.hp.report.kpis"
    _columns = {
        'type': fields.selection([
                    ('3d', '3D Design'),
                    ('casting', 'Casting'),
                    ('assembling', 'Assembling'),
                    ('setting', 'Setting'),
                    ('aggregate','General'),
                    ], 'Report Type',select=True,required=True),
        'option': fields.selection([
                    ('month', 'Month Report'),
                    ('year', 'Year Report'),
                    ('other', 'Other reports'),
                    ], 'Option',select=True,required=True),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'month': fields.many2one('account.period', 'Month From'),
        'month_from': fields.many2one('account.period', 'Month From'),
        'month_to': fields.many2one('account.period', 'Month To'),
     }

    def action_print(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_from','date_to','type','option','month', 'month_from','month_to'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hp.report.kpis'
        type = res['type']
        if type == '3d':
            datas['line'] = self.print_hp_report_kpis_3d(cr, uid, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_3d',
                'datas'         : datas,
           }
        elif type =='casting':
            datas['line'] = self.print_hp_report_kpis_casting(cr, uid, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_casting',
                'datas'         : datas,
                }
        elif type =='assembling':
            datas['line'] = self.print_hp_report_kpis_assembling(cr, uid, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_assembling',
                'datas'         : datas,
                }
        elif type =='setting':
            datas['line'] = self.print_hp_report_kpis_setting(cr, uid, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_setting',
                'datas'         : datas,
           }
        elif type =='aggregate':
            if res['option'] == 'month':
                datas['line'] = self.print_hp_report_kpis_aggregate(cr, uid, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
                return {
                    'type'          : 'ir.actions.report.xml',
                    'report_name'   : 'wizard_hp_report_kpis_aggregate',
                    'datas'         : datas,
               }
            elif res['option'] == 'year':
                datas['line'] = self.print_hp_report_kpis_aggregate(cr, uid, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
                return {
                    'type'          : 'ir.actions.report.xml',
                    'report_name'   : 'wizard_hp_report_kpis_aggregate_year',
                    'datas'         : datas,
                }
            else:
                raise osv.except_osv(('Wanning'),('General report supports only the month and year!'))
           


            
    def print_hp_report_kpis_3d(self, cr, uid, type, date_from, date_to, month, month_from, month_to):
        #report week
        
        name_report = ''
        if type == 'month':
            period = self.pool.get('account.period').browse(cr, uid, month[0])
            print month
            name_report = period.name
            date_from = period.date_start
            date_to = period.date_stop
        #report month
        elif type == 'year':
            period_from = self.pool.get('account.period').browse(cr, uid,month_from[0])
            period_to = self.pool.get('account.period').browse(cr, uid,month_to[0])
            name_report = period_from.name+' - '+period_to.name
            date_from = period_from.date_start
            date_to = period_to.date_stop
        stt = 0
        
        line_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.type','=','3d'),('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('parent_id.state','=','confirmed')])
        line_objs = self.pool.get('hpusa.3d.report.line').browse(cr, uid, line_ids)
        #group
        groups = {}
        result = []
        for line_3d in line_objs:
            if not groups.has_key(line_3d.parent_id.designer_id.name):
                groups[line_3d.parent_id.designer_id.name] = []
            groups[line_3d.parent_id.designer_id.name].append(line_3d)
        for key in sorted(groups):
            arr = []
            employee_name = key
            s_i = 0
            s_ii = 0
            s_iii = 0
            s_iv = 0
            s_v = 0
            s_vi = 0
            s_level = 0
            s_coeff = 0
            s_times = 0 
            s_co_times = 0
            s_total_co = 0
            s_target = 0
            s_compare = 0
            
            for line_3d in groups[key]:
                stt = stt + 1
                #sale order
                sale_line = self.pool.get('sale.order.line').search(cr, uid, [('product_id','=',line_3d.product_id.id)])
                sale_name = ''
                if(sale_line):
                    sale_name = self.pool.get('sale.order.line').browse(cr, uid, sale_line[0]).order_id.name
                #add line report
                i = 0
                ii = 0
                iii = 0
                iv = 0
                v = 0
                vi = 0
                #% complete
                if(line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.name == 'I'):
                    i = line_3d.complete
                elif(line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.name == 'II'):
                    ii = line_3d.complete
                elif(line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.name == 'III'):
                    iii = line_3d.complete
                elif(line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.name == 'IV'):
                    iv = line_3d.complete
                elif(line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.name == 'V'):
                    v = line_3d.complete
                elif(line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.name == 'VI'):
                    vi = line_3d.complete
                #get tagert
                target = 0
                if(line_3d.product_id._3d_difficulty_level):
                    tagert_ids = self.pool.get('hpusa.kpis.target.3d.line').search(cr, uid, [('level','=',line_3d.product_id._3d_difficulty_level.id)])
                    if(tagert_ids):
                        target = self.pool.get('hpusa.kpis.target.3d.line').browse(cr, uid, tagert_ids[0]).target
                        
                coefficient_lv = line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.coefficient or 0
                total_coeff_lv = (i + ii + iii + iv + v + vi) * coefficient_lv # (6)=(4)*(5)
                #times
                _3d_times = line_3d.product_id._3d_design_times and line_3d.product_id._3d_design_times.name or 0
                coefficient_3d_times = line_3d.product_id._3d_design_times and line_3d.product_id._3d_design_times.coefficient or 0
                compare = 0
                if target > 0:
                    compare = (total_coeff_lv * _3d_times * coefficient_3d_times)/target
                s_i += i
                s_ii += ii
                s_iii += iii
                s_iv += iv
                s_v += v
                s_vi += vi
                s_level += coefficient_lv
                s_coeff += coefficient_lv
                s_times += _3d_times
                s_co_times += coefficient_3d_times
                s_total_co += total_coeff_lv * _3d_times * coefficient_3d_times
                s_target += target
                s_compare += compare
                arr.append({
                            'stt'        :  stt,
                            'date'       :  line_3d.parent_id.report_date,
                            'employee'   :  employee_name,
                            'sale_order' :  sale_name,
                            'i'          :  i,
                            'ii'         :  ii,
                            'iii'        :  iii,
                            'iv'         :  iv,
                            'v'          :  v,
                            'vi'         :  vi,
                            'co_level'   :  coefficient_lv,
                            'tt_coeff_lv':  total_coeff_lv,
                            '_3d_times'  :  _3d_times,
                            'co_3d_times':  coefficient_3d_times,
                            'total_co'   :  total_coeff_lv * _3d_times * coefficient_3d_times, # (9)=(6)*(7)*(8)
                            'target_date':  target,
                            'compare'    :  compare,#(11)=(9)/(10)
                            })
            re = {'line': arr, 's_i': s_i, 's_ii': s_ii, 's_iii': s_iii, 's_iv': s_iv, 's_v': s_v, 's_vi': s_vi, 's_level': s_level, 's_coeff': s_coeff, 's_times': s_times, 's_co_times': s_co_times, 's_total_co': s_total_co, 's_target': s_target, 's_compare': s_compare}
            result.append(re)
        return {'name': name_report, 'result': result}
    
    def print_hp_report_kpis_casting(self, cr, uid, type, date_from, date_to, month, month_from, month_to):
        #report week
        name_report = ''
        if type == 'month':
            period = self.pool.get('account.period').browse(cr, uid, month[0])
            print month
            name_report = period.name
            date_from = period.date_start
            date_to = period.date_stop
        #report month
        elif type == 'year':
            period_from = self.pool.get('account.period').browse(cr, uid,month_from[0])
            period_to = self.pool.get('account.period').browse(cr, uid,month_to[0])
            name_report = period_from.name+' - '+period_to.name
            date_from = period_from.date_start
            date_to = period_to.date_stop
        casting_ids = self.pool.get('hpusa.daily.report.casting').search(cr, uid, [('type','=','casting'),('report_date','>=',date_from),('report_date','<=',date_to),('state','=','confirmed')])
        _casting = self.pool.get('hpusa.daily.report.casting').browse(cr, uid, casting_ids)
        arr = []
        stt = 0
        s_1 = 0
        s_2 = 0
        s_3 = 0
        s_4 = 0
        s_coff = 0
        s_total_coeff = 0
        s_target = 0
        s_compare = 0
        for obj_casting in _casting:
            for line_casting in obj_casting.line_ids:
                stt = stt + 1
                #sale order
                sale_line = self.pool.get('sale.order.line').search(cr, uid, [('product_id','=',line_casting.product_id.id)])
                sale_name = ''
                if(sale_line):
                    sale_name = self.pool.get('sale.order.line').browse(cr, uid, sale_line[0]).order_id.name
                    #add line report
                _1_time = 0;
                _2_times = 0;
                _3_times = 0;
                _4_times = 0;
                #get times casting
                if(line_casting.product_id.casting_times and line_casting.product_id.casting_times.name == 1):
                    _1_time = 1
                elif(line_casting.product_id.casting_times and line_casting.product_id.casting_times.name == 2):
                    _2_times = 1
                elif(line_casting.product_id.casting_times and line_casting.product_id.casting_times.name == 3):
                    _3_times = 1
                elif(line_casting.product_id.casting_times and line_casting.product_id.casting_times.name >= 4):
                    _4_times = 1
                
                coefficient = 0
                if(line_casting.product_id.casting_type and line_casting.product_id.casting_type == 'gold' and line_casting.product_id.casting_times):
                    coefficient = line_casting.product_id.casting_times.coefficient_gold
                elif(line_casting.product_id.casting_type and line_casting.product_id.casting_type == 'platinum' and line_casting.product_id.casting_times):
                    coefficient = line_casting.product_id.casting_times.coefficient_pt
                total_coeff = (_1_time + _2_times + _3_times + _4_times) * coefficient # (6)=(4)*(5)
#                    #get tagert
                target = 0
                if(line_casting.product_id.casting_type):
                    tagert_ids = self.pool.get('hpusa.kpis.target.casting.line').search(cr, uid, [('casting_type','=',line_casting.product_id.casting_type)])
                    if(tagert_ids):
                        target = self.pool.get('hpusa.kpis.target.casting.line').browse(cr, uid, tagert_ids[0]).target
                s_1 += _1_time
                s_2 += _2_times
                s_3 += _3_times
                s_4 += _4_times
                s_coff += coefficient
                s_total_coeff += total_coeff
                s_target += target
                s_compare += round(target > 0 and total_coeff / target or 0, 2)
                
                arr.append({
                            'stt'        :  stt,
                            'date'       :  obj_casting.report_date,
                            'employee'   :  line_casting.worker.name,
                            'sale_order' :  sale_name,
                            '_1_time'    :  _1_time,
                            '_2_times'   :  _2_times,
                            '_3_times'   :  _3_times,
                            '_4_times'   :  _4_times,
                            'coefficient':  coefficient,
                            'total_coeff':  total_coeff,
                            'target'     :  target,
                            'compare'    :  round(target > 0 and total_coeff / target or 0, 2), #(8)=(6)/(7),
                            }) 
        return {'name': name_report, 'line': arr, 's_1': s_1, 's_2': s_2, 's_3': s_3, 's_4': s_4, 's_coff': s_coff, 's_total_coeff': s_total_coeff, 's_target': s_target, 's_compare': s_compare}
    
    
    def print_hp_report_kpis_assembling(self, cr, uid, type, date_from, date_to, month, month_from, month_to):
        #report week
        arr = []
        name_report = ''
        if type == 'month':
            period = self.pool.get('account.period').browse(cr, uid, month[0])
            print month
            name_report = period.name
            date_from = period.date_start
            date_to = period.date_stop
        #report month
        elif type == 'year':
            period_from = self.pool.get('account.period').browse(cr, uid,month_from[0])
            period_to = self.pool.get('account.period').browse(cr, uid,month_to[0])
            name_report = period_from.name+' - '+period_to.name
            date_from = period_from.date_start
            date_to = period_to.date_stop
        assembling_ids = self.pool.get('hpusa.daily.report.assembling').search(cr, uid, [('type','=','assembling'),('report_date','>=',date_from),('report_date','<=',date_to),('state','=','confirmed')])
        assembling = self.pool.get('hpusa.daily.report.assembling').browse(cr, uid, assembling_ids)
        stt = 0
        s_i = 0
        s_ii = 0
        s_iii = 0
        s_iv = 0
        s_v = 0
        s_vi = 0
        s_percent = 0
        s_coeff = 0
        s_target = 0
        s_compare = 0
        s_total_coeff = 0
        for obj_assembling in assembling:
            for line_assembling in obj_assembling.line_ids:
                stt = stt + 1
                #sale order
                sale_line = self.pool.get('sale.order.line').search(cr, uid, [('product_id','=',line_assembling.product_id.id)])
                sale_name = '' 
                if(sale_line):
                    sale_name = self.pool.get('sale.order.line').browse(cr, uid, sale_line[0]).order_id.name
                    #add line report
                i = 0
                ii = 0
                iii = 0
                iv = 0
                v = 0
                vi = 0
                #% complete
                if(line_assembling.product_id.ass_difficulty_level and line_assembling.product_id.ass_difficulty_level.name == 'I'):
                    i = 1
                elif(line_assembling.product_id.ass_difficulty_level and line_assembling.product_id.ass_difficulty_level.name == 'II'):
                    ii = 1
                elif(line_assembling.product_id.ass_difficulty_level and line_assembling.product_id.ass_difficulty_level.name == 'III'):
                    iii = 1
                elif(line_assembling.product_id.ass_difficulty_level and line_assembling.product_id.ass_difficulty_level.name == 'IV'):
                    iv = 1
                elif(line_assembling.product_id.ass_difficulty_level and line_assembling.product_id.ass_difficulty_level.name == 'V'):
                    v = 1
                elif(line_assembling.product_id.ass_difficulty_level and line_assembling.product_id.ass_difficulty_level.name == 'VI'):
                    vi = 1
                #get tagert
                target = 0
                if(line_assembling.product_id.ass_difficulty_level):
                    tagert_ids = self.pool.get('hpusa.kpis.target.assembling.line').search(cr, uid, [('level','=',line_assembling.product_id.ass_difficulty_level.id)])
                    if(tagert_ids):
                        target = self.pool.get('hpusa.kpis.target.assembling.line').browse(cr, uid, tagert_ids[0]).target
                coeff =  line_assembling.product_id.ass_difficulty_level and line_assembling.product_id.ass_difficulty_level.coefficient or 0 
                total_coeff = (i + ii + iii + iv + v + vi) * coeff
                
                s_i += i
                s_ii += ii
                s_iii += iii
                s_iv += iv
                s_v += v
                s_vi += vi
                s_percent += line_assembling.complete
                s_coeff += coeff
                s_total_coeff += total_coeff
                s_target += target
                s_compare += round(target > 0 and total_coeff/target or 0,2)
                
                arr.append({
                            'stt'        :  stt,
                            'date'       :  obj_assembling.report_date,
                            'employee'   :  line_assembling.worker.name,
                            'sale_order' :  sale_name,
                            'i'          :  i,
                            'ii'         :  ii,
                            'iii'        :  iii,
                            'iv'         :  iv,
                            'v'          :  v,
                            'vi'         :  vi,
                            'percent'    :  line_assembling.complete,
                            'coeff'      :  coeff,
                            'total_coeff':  total_coeff,
                            'target'     :  target,
                            'compare'    :  round(target > 0 and total_coeff/target or 0,2),#(8)=(6)/(7)
                            })
        return {'name': name_report, 'line': arr, 's_i': s_i, 's_ii': s_ii, 's_iii': s_iii, 's_iv': s_iv, 's_v': s_v, 's_vi': s_vi,
                's_percent': s_percent, 's_coeff': s_coeff, 's_total_coeff': s_total_coeff, 's_target': s_target, 's_compare': s_compare}
    
    
    def print_hp_report_kpis_setting(self, cr, uid, type, date_from, date_to, month, month_from, month_to):
        #report week
        arr = []
        name_report = ''
        if type == 'month':
            period = self.pool.get('account.period').browse(cr, uid, month[0])
            print month
            name_report = period.name
            date_from = period.date_start
            date_to = period.date_stop
        #report month
        elif type == 'year':
            period_from = self.pool.get('account.period').browse(cr, uid,month_from[0])
            period_to = self.pool.get('account.period').browse(cr, uid,month_to[0])
            name_report = period_from.name+' - '+period_to.name
            date_from = period_from.date_start
            date_to = period_to.date_stop
        setting_ids = self.pool.get('hpusa.daily.report.setting').search(cr, uid, [('type','=','setting'),('report_date','>=',date_from),('report_date','<=',date_to),('state','=','confirmed')])
        setting = self.pool.get('hpusa.daily.report.setting').browse(cr, uid, setting_ids)
        stt = 0
        s_i = 0
        s_ii = 0
        s_iii = 0
        s_iv = 0
        s_v = 0
        s_vi = 0
        s_vii = 0
        s_viii = 0
        s_ix = 0
        s_per = 0
        s_coeff = 0
        s_total_coeff = 0
        s_target = 0
        s_compare = 0
        for obj_setting in setting:
            for line_setting in obj_setting.line_ids:
                stt = stt + 1
                #sale order
                sale_line = self.pool.get('sale.order.line').search(cr, uid, [('product_id','=',line_setting.product_id.id)])
                sale_name = ''
                if(sale_line):
                    sale_name = self.pool.get('sale.order.line').browse(cr, uid, sale_line[0]).order_id.name
                    #add line report
                I = 0
                II = 0
                III = 0
                IV = 0
                V = 0
                VI = 0
                VII = 0
                VIII = 0
                IX = 0
                #% complete
                if(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'I'):
                    I = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'II'):
                    II = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'III'):
                    III = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'IV'):
                    IV = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'V'):
                    V = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'VI'):
                    VI = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'VII'):
                    VII = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'VIII'):
                    VIII = 1
                elif(line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.name == 'IX'):
                    IX = 1
                percent = line_setting.complete
                coeff =  line_setting.product_id.setting_difficulty_level and line_setting.product_id.setting_difficulty_level.coefficient or 0 
                total_coeff = (I + II + III + IV + V + VI + VII + VIII + IX) * percent * coeff #(7)=(4)*(5)*(6)
                #get tagert
                target = 0
                if(line_setting.product_id.setting_difficulty_level):
                    tagert_ids = self.pool.get('hpusa.kpis.target.setting.line').search(cr, uid, [('level','=',line_setting.product_id.setting_difficulty_level.id)])
                    if(tagert_ids):
                        target = self.pool.get('hpusa.kpis.target.setting.line').browse(cr, uid, tagert_ids[0]).target
                s_i += I
                s_ii += II
                s_iii += III
                s_iv += IV
                s_v += V
                s_vi += VI
                s_vii += VII
                s_viii += VIII
                s_ix += IV
                s_per += percent
                s_coeff += coeff
                s_total_coeff += total_coeff
                s_target += target
                s_compare += target > 0 and total_coeff/target or 0
                arr.append({
                            'stt'        :  stt,
                            'date'       :  obj_setting.report_date,
                            'employee'   :  line_setting.worker.name,
                            'sale_order' :  sale_name,
                            'I'          :  I,
                            'II'         :  II,
                            'III'        :  III,
                            'IV'         :  IV,
                            'V'          :  V,
                            'VI'         :  VI,
                            'VII'        :  VII,
                            'VIII'       :  VIII,
                            'IX'         :  IX,
                            'percent'    :  percent,
                            'coeff'      :  coeff,
                            'total_coeff':  total_coeff,
                            'target'     :  target,
                            'compare'    :  target > 0 and total_coeff/target or 0,#(8)=(6)/(7)
                            })
        return {'name': name_report, 'line': arr, 's_i': s_i, 's_ii': s_ii, 's_iii': s_iii, 's_iv': s_iv, 's_v': s_v,
                's_vi': s_vi, 's_vii': s_vii, 's_viii': s_viii, 's_ix': s_ix, 's_per': s_per, 's_coeff': s_coeff, 's_total_coeff': s_total_coeff,
                's_target': s_target, 's_compare': s_compare}

        
    def print_hp_report_kpis_aggregate(self, cr, uid, type, date_from, date_to, month, month_from, month_to):
        #report week
        arr = []
        name_report = ''
        if type == 'month':
            period = self.pool.get('account.period').browse(cr, uid, month[0])
            name_report = period.name
            date_from = period.date_start
            date_to = period.date_stop
            qty_3d_1_1 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 1)
            qty_3d_1_2 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 2)
            qty_3d_1_3 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 3)
            qty_3d_1_4 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 4)
            
            qty_3d_2_1 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 1)
            qty_3d_2_2 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 2)
            qty_3d_2_3 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 3)
            qty_3d_2_4 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 4)
            
            qty_3d_3_1 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 1)
            qty_3d_3_2 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 2)
            qty_3d_3_3 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 3)
            qty_3d_3_4 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 4)

            qty_3d_4_1 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 1)
            qty_3d_4_2 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 2)
            qty_3d_4_3 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 3)
            qty_3d_4_4 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 4)

            qty_3d_easy_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 1)
            qty_3d_easy_2 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 2)
            qty_3d_easy_3 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 3)
            qty_3d_easy_4 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 4)

            qty_3d_medium_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 1)
            qty_3d_medium_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 2)
            qty_3d_medium_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 3)
            qty_3d_medium_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 3)

            qty_3d_medium_hard_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 1)
            qty_3d_medium_hard_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 2)
            qty_3d_medium_hard_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 3)
            qty_3d_medium_hard_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 4)

            qty_3d_hard_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 1)
            qty_3d_hard_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 2)
            qty_3d_hard_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 3)
            qty_3d_hard_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 4)

            qty_3d_very_hard_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 1)
            qty_3d_very_hard_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 2)
            qty_3d_very_hard_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 3)
            qty_3d_very_hard_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 4)
            
            qty_casting_1_1 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 1)
            qty_casting_1_2 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 2)
            qty_casting_1_3 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 3)
            qty_casting_1_4 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 4)
            
            qty_casting_2_1 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 1)
            qty_casting_2_2 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 2)
            qty_casting_2_3 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 3)
            qty_casting_2_4 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 4)
            
            qty_casting_3_1 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 1)
            qty_casting_3_2 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 2)
            qty_casting_3_3 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 3)
            qty_casting_3_4 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 4)
            
            qty_casting_4_1 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 1)
            qty_casting_4_2 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 2)
            qty_casting_4_3 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 3)
            qty_casting_4_4 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 4)
            
            qty_assembling_easy_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 1)
            qty_assembling_easy_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 2)
            qty_assembling_easy_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 3)
            qty_assembling_easy_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 4)
            
            qty_assembling_medium_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 1)
            qty_assembling_medium_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 2)
            qty_assembling_medium_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 3)
            qty_assembling_medium_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 4)
            
            qty_assembling_hard_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 1)
            qty_assembling_hard_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 2)
            qty_assembling_hard_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 3)
            qty_assembling_hard_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 4)
            
            qty_assembling_very_hard_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 1)
            qty_assembling_very_hard_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 2)
            qty_assembling_very_hard_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 3)
            qty_assembling_very_hard_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 4)
            
            qty_setting_i_1 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 1)
            qty_setting_i_2 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 2)
            qty_setting_i_3 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 3)
            qty_setting_i_4 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 4)
            
            qty_setting_ii_1 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 1)
            qty_setting_ii_2 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 2)
            qty_setting_ii_3 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 3)
            qty_setting_ii_4 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 4)
            
            qty_setting_iii_1 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 1)
            qty_setting_iii_2 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 2)
            qty_setting_iii_3 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 3)
            qty_setting_iii_4 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 4)
            
            qty_setting_iv_1 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 1)
            qty_setting_iv_2 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 2)
            qty_setting_iv_3 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 3)
            qty_setting_iv_4 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 4)
            
            qty_setting_v_1 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 1)
            qty_setting_v_2 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 2)
            qty_setting_v_3 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 3)
            qty_setting_v_4 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 4)
            
            qty_setting_vi_1 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 1)
            qty_setting_vi_2 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 2)
            qty_setting_vi_3 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 3)
            qty_setting_vi_4 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 4)
            
            qty_setting_vii_1 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 1)
            qty_setting_vii_2 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 2)
            qty_setting_vii_3 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 3)
            qty_setting_vii_4 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 4)
            
            qty_setting_viii_1 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 1)
            qty_setting_viii_2 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 2)
            qty_setting_viii_3 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 3)
            qty_setting_viii_4 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 4)
            
            qty_setting_ix_1 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 1)
            qty_setting_ix_2 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 2)
            qty_setting_ix_3 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 3)
            qty_setting_ix_4 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 4)
                      
            
            arr = {
                      'coeff_3d_1': self._3d_times(cr, uid, '=', 1),
                      'qty_3d_1_1': qty_3d_1_1,
                      'qty_3d_1_2': qty_3d_1_2,
                      'qty_3d_1_3': qty_3d_1_3,
                      'qty_3d_1_4': qty_3d_1_4,
                      'qty_3d_1_total': qty_3d_1_1 + qty_3d_1_2 + qty_3d_1_3 +qty_3d_1_4,
                      'emp_3d_1': self._3d_employee_times(cr, uid, date_from, date_to, '=', 1),
                      'target_3d_1': 0,
                      
                      'coeff_3d_2': self._3d_times(cr, uid, '=', 2),
                      'qty_3d_2_1': qty_3d_2_1,
                      'qty_3d_2_2': qty_3d_2_2,
                      'qty_3d_2_3': qty_3d_2_3,
                      'qty_3d_2_4': qty_3d_2_4,
                      'qty_3d_2_total': qty_3d_2_1 + qty_3d_2_2 + qty_3d_2_3 + qty_3d_2_4,
                      'emp_3d_2': self._3d_employee_times(cr, uid, date_from, date_to, '=', 2),
                      'target_3d_2': 0,
                      
                      'coeff_3d_3': self._3d_times(cr, uid, '=', 3),
                      'qty_3d_3_1': qty_3d_3_1,
                      'qty_3d_3_2': qty_3d_3_2,
                      'qty_3d_3_3': qty_3d_3_3,
                      'qty_3d_3_4': qty_3d_3_4,
                      'qty_3d_3_total': qty_3d_3_1 + qty_3d_3_2 + qty_3d_3_3 + qty_3d_3_4,
                      'emp_3d_3': self._3d_employee_times(cr, uid, date_from, date_to, '=', 3),
                      'target_3d_3': 0,
                      
                      'coeff_3d_4': self._3d_times(cr, uid, '>=', 4),
                      'qty_3d_4_1': qty_3d_4_1,
                      'qty_3d_4_2': qty_3d_4_2,
                      'qty_3d_4_3': qty_3d_4_3,
                      'qty_3d_4_4': qty_3d_4_4,
                      'qty_3d_4_total': qty_3d_4_1 + qty_3d_4_2 + qty_3d_4_3 + qty_3d_4_4,
                      'emp_3d_4': self._3d_employee_times(cr, uid, date_from, date_to, '>=', 4),
                      'target_3d_4': 0,
                      
                      'coeff_3d_easy': self._3d_level(cr, uid, 'Easy'),
                      'qty_3d_easy_1':  qty_3d_easy_1,
                      'qty_3d_easy_2':  qty_3d_easy_2,
                      'qty_3d_easy_3':  qty_3d_easy_2,
                      'qty_3d_easy_4':  qty_3d_easy_4,
                      'qty_3d_easy_total':  qty_3d_easy_1 + qty_3d_easy_2 + qty_3d_easy_3 + qty_3d_easy_4,
                      'emp_3d_easy': self._3d_employee_level(cr, uid, date_from, date_to, 'Easy'),
                      'target_3d_easy': self._3d_target(cr, uid, 'Easy'),
                      
                      'coeff_3d_medium': self._3d_level(cr, uid, 'Medium'),
                      'qty_3d_medium_1': qty_3d_medium_1,
                      'qty_3d_medium_2': qty_3d_medium_2,
                      'qty_3d_medium_3': qty_3d_medium_3,
                      'qty_3d_medium_4': qty_3d_medium_4,
                      'qty_3d_medium_total': qty_3d_medium_1 + qty_3d_medium_2 + qty_3d_medium_3 + qty_3d_medium_4,
                      'emp_3d_medium': self._3d_employee_level(cr, uid, date_from, date_to, 'Medium'),
                      'target_3d_medium': self._3d_target(cr, uid, 'Medium'),
                      
                      'coeff_3d_medium_hard': self._3d_level(cr, uid, 'Medium - Hard'),
                      'qty_3d_medium_hard_1': qty_3d_medium_hard_1,
                      'qty_3d_medium_hard_2': qty_3d_medium_hard_2,
                      'qty_3d_medium_hard_3': qty_3d_medium_hard_3,
                      'qty_3d_medium_hard_4': qty_3d_medium_hard_4,
                      'qty_3d_medium_hard_total': qty_3d_medium_hard_4,
                      'emp_3d_medium_hard': self._3d_employee_level(cr, uid, date_from, date_to, 'Medium - Hard'),
                      'target_3d_medium_hard': self._3d_target(cr, uid, 'Medium - Hard'),
                      
                      'coeff_3d_hard': self._3d_level(cr, uid, 'Hard'),
                      'qty_3d_hard_1': qty_3d_hard_1,
                      'qty_3d_hard_2': qty_3d_hard_2,
                      'qty_3d_hard_3': qty_3d_hard_3,
                      'qty_3d_hard_4': qty_3d_hard_4,
                      'qty_3d_hard_total': qty_3d_hard_1 + qty_3d_hard_2 + qty_3d_hard_3 + qty_3d_hard_4,
                      'emp_3d_hard': self._3d_employee_level(cr, uid, date_from, date_to, 'Hard'),
                      'target_3d_hard': self._3d_target(cr, uid, 'Hard'),
                      
                      'coeff_3d_very_hard': self._3d_level(cr, uid, 'Very Hard'),
                      'qty_3d_very_hard_1': qty_3d_very_hard_1,
                      'qty_3d_very_hard_2': qty_3d_very_hard_2,
                      'qty_3d_very_hard_3': qty_3d_very_hard_3,
                      'qty_3d_very_hard_4': qty_3d_very_hard_4,
                      'qty_3d_very_hard_total': qty_3d_very_hard_1 + qty_3d_very_hard_2 + qty_3d_very_hard_3 + qty_3d_very_hard_4,
                      'emp_3d_very_hard': self._3d_employee_level(cr, uid, date_from, date_to, 'Very Hard'),
                      'target_3d_very_hard': self._3d_target(cr, uid, 'Very Hard'),
                      
                      
                      'coeff_casting_1' : self.casting(cr, uid, '=', 1),
                      'qty_casting_1_1': qty_casting_1_1,
                      'qty_casting_1_2': qty_casting_1_2,
                      'qty_casting_1_3': qty_casting_1_3,
                      'qty_casting_1_4': qty_casting_1_4,
                      'qty_casting_1_total': qty_casting_1_1 + qty_casting_1_2 + qty_casting_1_3 + qty_casting_1_4,
                      'emp_casting_1': self.casting_employee(cr, uid, date_from, date_to, '=', 1),
                      'target_casting_1': 0,
                      
                      'coeff_casting_2' : self.casting(cr, uid, '=', 2),
                      'qty_casting_2_1': qty_casting_2_1,
                      'qty_casting_2_2': qty_casting_2_2,
                      'qty_casting_2_3': qty_casting_2_3,
                      'qty_casting_2_4': qty_casting_2_4,
                      'qty_casting_2_total': qty_casting_2_1 + qty_casting_2_2 + qty_casting_2_3 + qty_casting_2_4,
                      'emp_casting_2': self.casting_employee(cr, uid, date_from, date_to, '=', 2),
                      'target_casting_2': 0,
                      
                      'coeff_casting_3' : self.casting(cr, uid, '=', 3),
                      'qty_casting_3_1': qty_casting_3_1,
                      'qty_casting_3_2': qty_casting_3_2,
                      'qty_casting_3_3': qty_casting_3_3,
                      'qty_casting_3_4':  qty_casting_3_4,
                      'qty_casting_3_total':  qty_casting_3_1 + qty_casting_3_2 + qty_casting_3_3 + qty_casting_3_4,
                      'emp_casting_3': self.casting_employee(cr, uid, date_from, date_to, '=', 3),
                      'target_casting_3': 0,
                      
                      'coeff_casting_4' : self.casting(cr, uid, '>=', 4),
                      'qty_casting_4_1':  qty_casting_4_1,
                      'qty_casting_4_2': qty_casting_4_2,
                      'qty_casting_4_3': qty_casting_4_3,
                      'qty_casting_4_4': qty_casting_4_4,
                      'qty_casting_4_total': qty_casting_4_1 + qty_casting_4_2 + qty_casting_4_3 + qty_casting_4_4,
                      'emp_casting_4': self.casting_employee(cr, uid, date_from, date_to, '=', 4),
                      'target_casting_4': 0,
                      
                      
                      'coeff_assembling_easy': self.assembling(cr, uid, 'Easy'),
                      'qty_assembling_easy_1': qty_assembling_easy_1,
                      'qty_assembling_easy_2': qty_assembling_easy_2,
                      'qty_assembling_easy_3': qty_assembling_easy_3,
                      'qty_assembling_easy_4': qty_assembling_easy_4,
                      'qty_assembling_easy_total': qty_assembling_easy_1 + qty_assembling_easy_2 + qty_assembling_easy_3 + qty_assembling_easy_4,
                      'emp_assembling_easy'  : self.assembling_employee(cr, uid, date_from, date_to, 'Easy'),
                      'target_assembling_easy': self.target_assembling(cr, uid, 'Easy'),
                      
                      'coeff_assembling_medium': self.assembling(cr, uid, 'Medium'),
                      'qty_assembling_medium_1': qty_assembling_medium_1,
                      'qty_assembling_medium_2': qty_assembling_medium_2,
                      'qty_assembling_medium_3': qty_assembling_medium_3,
                      'qty_assembling_medium_4': qty_assembling_medium_4,
                      'qty_assembling_medium_total': qty_assembling_medium_1 + qty_assembling_medium_2 + qty_assembling_medium_3 + qty_assembling_medium_4,
                      'emp_assembling_medium'  : self.assembling_employee(cr, uid, date_from, date_to, 'Medium'),
                      'target_assembling_medium': self.target_assembling(cr, uid, 'Medium'),
                      
                      'coeff_assembling_hard': self.assembling(cr, uid, 'Hard'),
                      'qty_assembling_hard_1': qty_assembling_hard_1,
                      'qty_assembling_hard_2': qty_assembling_hard_2,
                      'qty_assembling_hard_3': qty_assembling_hard_3,
                      'qty_assembling_hard_4': qty_assembling_hard_4,
                      'qty_assembling_hard_total': qty_assembling_hard_1 + qty_assembling_hard_2 + qty_assembling_hard_3 + qty_assembling_hard_4,
                      'emp_assembling_hard'  : self.assembling_employee(cr, uid, date_from, date_to, 'Hard'),
                      'target_assembling_hard': self.target_assembling(cr, uid, 'Hard'),
                      
                      'coeff_assembling_very_hard': self.assembling(cr, uid, 'Very Hard'),
                      'qty_assembling_very_hard_1': qty_assembling_very_hard_1,
                      'qty_assembling_very_hard_2': qty_assembling_very_hard_2,
                      'qty_assembling_very_hard_3': qty_assembling_very_hard_3,
                      'qty_assembling_very_hard_4': qty_assembling_very_hard_4,
                      'qty_assembling_very_hard_total': qty_assembling_very_hard_1 + qty_assembling_very_hard_2 + qty_assembling_very_hard_3 + qty_assembling_very_hard_4,
                      'emp_assembling_very_hard'  : self.assembling_employee(cr, uid, date_from, date_to, 'Very Hard'),
                      'target_assembling_very_hard': self.target_assembling(cr, uid, 'Very Hard'),
                      
                      
                      'coeff_setting_i': self.setting(cr, uid, 'I'),
                      'qty_setting_i_1': qty_setting_i_1,
                      'qty_setting_i_2': qty_setting_i_2,
                      'qty_setting_i_3': qty_setting_i_3,
                      'qty_setting_i_4': qty_setting_i_4,
                      'qty_setting_i_total': qty_setting_i_1 + qty_setting_i_2 + qty_setting_i_3 + qty_setting_i_4,
                      'emp_setting_i': self.setting_employee(cr, uid, date_from, date_to, 'I'),
                      'target_setting_i': self.target_setting(cr, uid, 'I'),
                      
                      'coeff_setting_ii': self.setting(cr, uid, 'II'),
                      'qty_setting_ii_1': qty_setting_ii_1,
                      'qty_setting_ii_2': qty_setting_ii_2,
                      'qty_setting_ii_3': qty_setting_ii_3,
                      'qty_setting_ii_4': qty_setting_ii_4,
                      'qty_setting_ii_total': qty_setting_ii_1 + qty_setting_ii_2 + qty_setting_ii_3 + qty_setting_ii_4,
                      'emp_setting_ii': self.setting_employee(cr, uid, date_from, date_to, 'II'),
                      'target_setting_ii': self.target_setting(cr, uid, 'II'),
                      
                      'coeff_setting_iii': self.setting(cr, uid, 'III'),
                      'qty_setting_iii_1': qty_setting_iii_1,
                      'qty_setting_iii_2': qty_setting_iii_2,
                      'qty_setting_iii_3': qty_setting_iii_3,
                      'qty_setting_iii_4': qty_setting_iii_4,
                      'qty_setting_iii_total': qty_setting_iii_1 + qty_setting_iii_2 + qty_setting_iii_3 + qty_setting_iii_4,
                      'emp_setting_iii': self.setting_employee(cr, uid, date_from, date_to, 'III'),
                      'target_setting_iii': self.target_setting(cr, uid, 'III'),
                      
                      'coeff_setting_iv': self.setting(cr, uid, 'IV'),
                      'qty_setting_iv_1': qty_setting_iv_1,
                      'qty_setting_iv_2': qty_setting_iv_2,
                      'qty_setting_iv_3': qty_setting_iv_3,
                      'qty_setting_iv_4': qty_setting_iv_4,
                      'qty_setting_iv_total': qty_setting_iv_1 + qty_setting_iv_2 + qty_setting_iv_3 + qty_setting_iv_4,
                      'emp_setting_iv': self.setting_employee(cr, uid, date_from, date_to, 'IV'),
                      'target_setting_iv': self.target_setting(cr, uid, 'IV'),
                      
                      'coeff_setting_v': self.setting(cr, uid, 'V'),
                      'qty_setting_v_1': qty_setting_v_1,
                      'qty_setting_v_2': qty_setting_v_2,
                      'qty_setting_v_3': qty_setting_v_3,
                      'qty_setting_v_4': qty_setting_v_4,
                      'qty_setting_v_total': qty_setting_v_1 + qty_setting_v_2 + qty_setting_v_3 + qty_setting_v_4,
                      'emp_setting_v': self.setting_employee(cr, uid, date_from, date_to, 'V'),
                      'target_setting_v': self.target_setting(cr, uid, 'V'),
                      
                      'coeff_setting_vi': self.setting(cr, uid, 'VI'),
                      'qty_setting_vi_1': qty_setting_vi_1,
                      'qty_setting_vi_2': qty_setting_vi_2,
                      'qty_setting_vi_3': qty_setting_vi_3,
                      'qty_setting_vi_4': qty_setting_vi_4,
                      'qty_setting_vi_total': qty_setting_vi_1 + qty_setting_vi_2 + qty_setting_vi_3 + qty_setting_vi_4,
                      'emp_setting_vi': self.setting_employee(cr, uid, date_from, date_to,'VI'),
                      'target_setting_vi': self.target_setting(cr, uid, 'VI'),
                      
                      'coeff_setting_vii': self.setting(cr, uid, 'VII'),
                      'qty_setting_vii_1': qty_setting_vii_1,
                      'qty_setting_vii_2': qty_setting_vii_2,
                      'qty_setting_vii_3': qty_setting_vii_3,
                      'qty_setting_vii_4': qty_setting_vii_4,
                      'qty_setting_vii_total': qty_setting_vii_1 + qty_setting_vii_2 + qty_setting_vii_3 + qty_setting_vii_4,
                      'emp_setting_vii': self.setting_employee(cr, uid, date_from, date_to, 'VII'),
                      'target_setting_vii': self.target_setting(cr, uid, 'VII'),
                      
                      'coeff_setting_viii': self.setting(cr, uid, 'VIII'),
                      'qty_setting_viii_1': qty_setting_viii_1,
                      'qty_setting_viii_2': qty_setting_viii_2,
                      'qty_setting_viii_3': qty_setting_viii_3,
                      'qty_setting_viii_4': qty_setting_viii_4,
                      'qty_setting_viii_total': qty_setting_viii_1 + qty_setting_viii_2 + qty_setting_viii_3 + qty_setting_viii_4,
                      'emp_setting_viii': self.setting_employee(cr, uid, date_from, date_to, 'VIII'),
                      'target_setting_viii': self.target_setting(cr, uid, 'VIII'),
                      
                      'coeff_setting_ix': self.setting(cr, uid, 'IX'),
                      'qty_setting_ix_1': qty_setting_ix_1,
                      'qty_setting_ix_2': qty_setting_ix_2,
                      'qty_setting_ix_3': qty_setting_ix_3,
                      'qty_setting_ix_4': qty_setting_ix_4,
                      'qty_setting_ix_total': qty_setting_ix_1 + qty_setting_ix_2 + qty_setting_ix_3 + qty_setting_ix_4,
                      'emp_setting_ix': self.setting_employee(cr, uid, date_from, date_to, 'IX'),
                      'target_setting_ix': self.target_setting(cr, uid, 'IX'),
                   }
            return {'name': name_report, 'line': arr}

        #report month
        elif type == 'year':
            period_from = self.pool.get('account.period').browse(cr, uid,month_from[0])
            period_to = self.pool.get('account.period').browse(cr, uid,month_to[0])
            name_report = period_from.name+' - '+period_to.name
            date_from = period_from.date_start
            date_to = period_to.date_stop
            
            qty_3d_1_1 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 1)
            qty_3d_1_2 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 2)
            qty_3d_1_3 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 3)
            qty_3d_1_4 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 4)
            qty_3d_1_5 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 5)
            qty_3d_1_6 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 6)
            qty_3d_1_7 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 7)
            qty_3d_1_8 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 8)
            qty_3d_1_9 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 9)
            qty_3d_1_10 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 10)
            qty_3d_1_11 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 11)
            qty_3d_1_12 = self.qty_3d_times(cr, uid, date_from, date_to, 1, type, 12)
            
            qty_3d_2_1 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 1)
            qty_3d_2_2 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 2)
            qty_3d_2_3 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 3)
            qty_3d_2_4 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 4)
            qty_3d_2_5 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 5)
            qty_3d_2_6 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 6)
            qty_3d_2_7 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 7)
            qty_3d_2_8 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 8)
            qty_3d_2_9 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 9)
            qty_3d_2_10 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 10)
            qty_3d_2_11 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 11)
            qty_3d_2_12 = self.qty_3d_times(cr, uid, date_from, date_to, 2, type, 12)
            
            qty_3d_3_1 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 1)
            qty_3d_3_2 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 2)
            qty_3d_3_3 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 3)
            qty_3d_3_4 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 4)
            qty_3d_3_5 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 5)
            qty_3d_3_6 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 6)
            qty_3d_3_7 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 7)
            qty_3d_3_8 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 8)
            qty_3d_3_9 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 9)
            qty_3d_3_10 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 10)
            qty_3d_3_11 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 11)
            qty_3d_3_12 = self.qty_3d_times(cr, uid, date_from, date_to, 3, type, 12)

            qty_3d_4_1 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 1)
            qty_3d_4_2 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 2)
            qty_3d_4_3 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 3)
            qty_3d_4_4 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 4)
            qty_3d_4_5 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 5)
            qty_3d_4_6 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 6)
            qty_3d_4_7 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 7)
            qty_3d_4_8 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 8)
            qty_3d_4_9 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 9)
            qty_3d_4_10 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 10)
            qty_3d_4_11 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 11)
            qty_3d_4_12 = self.qty_3d_times(cr, uid, date_from, date_to, 4, type, 12)

            qty_3d_easy_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 1)
            qty_3d_easy_2 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 2)
            qty_3d_easy_3 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 3)
            qty_3d_easy_4 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 4)
            qty_3d_easy_5 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 5)
            qty_3d_easy_6 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 6)
            qty_3d_easy_7 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 7)
            qty_3d_easy_8 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 8)
            qty_3d_easy_9 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 9)
            qty_3d_easy_10 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 10)
            qty_3d_easy_11 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 11)
            qty_3d_easy_12 =  self.qty_3d_level(cr, uid, date_from, date_to, 'Easy', type, 12)

            qty_3d_medium_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 1)
            qty_3d_medium_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 2)
            qty_3d_medium_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 3)
            qty_3d_medium_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 4)
            qty_3d_medium_5 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 5)
            qty_3d_medium_6 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 6)
            qty_3d_medium_7 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 7)
            qty_3d_medium_8 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 8)
            qty_3d_medium_9 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 9)
            qty_3d_medium_10 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 10)
            qty_3d_medium_11 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 11)
            qty_3d_medium_12 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium', type, 12)

            qty_3d_medium_hard_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 1)
            qty_3d_medium_hard_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 2)
            qty_3d_medium_hard_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 3)
            qty_3d_medium_hard_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 4)
            qty_3d_medium_hard_5 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 5)
            qty_3d_medium_hard_6 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 6)
            qty_3d_medium_hard_7 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 7)
            qty_3d_medium_hard_8 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 8)
            qty_3d_medium_hard_9 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 9)
            qty_3d_medium_hard_10 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 10)
            qty_3d_medium_hard_11 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 11)
            qty_3d_medium_hard_12 = self.qty_3d_level(cr, uid, date_from, date_to, 'Medium - Hard', type, 12)

            qty_3d_hard_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 1)
            qty_3d_hard_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 2)
            qty_3d_hard_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 3)
            qty_3d_hard_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 4)
            qty_3d_hard_5 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 5)
            qty_3d_hard_6 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 6)
            qty_3d_hard_7 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 7)
            qty_3d_hard_8 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 8)
            qty_3d_hard_9 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 9)
            qty_3d_hard_10 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 10)
            qty_3d_hard_11 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 11)
            qty_3d_hard_12 = self.qty_3d_level(cr, uid, date_from, date_to, 'Hard', type, 12)

            qty_3d_very_hard_1 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 1)
            qty_3d_very_hard_2 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 2)
            qty_3d_very_hard_3 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 3)
            qty_3d_very_hard_4 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 4)
            qty_3d_very_hard_5 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 5)
            qty_3d_very_hard_6 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 6)
            qty_3d_very_hard_7 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 7)
            qty_3d_very_hard_8 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 8)
            qty_3d_very_hard_9 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 9)
            qty_3d_very_hard_10 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 10)
            qty_3d_very_hard_11 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 11)
            qty_3d_very_hard_12 = self.qty_3d_level(cr, uid, date_from, date_to, 'Very Hard', type, 12)
            
            qty_casting_1_1 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 1)
            qty_casting_1_2 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 2)
            qty_casting_1_3 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 3)
            qty_casting_1_4 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 4)
            qty_casting_1_5 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 5)
            qty_casting_1_6 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 6)
            qty_casting_1_7 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 7)
            qty_casting_1_8 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 8)
            qty_casting_1_9 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 9)
            qty_casting_1_10 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 10)
            qty_casting_1_11 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 11)
            qty_casting_1_12 = self.qty_casting(cr, uid, date_from, date_to, 1, type, 12)
            
            qty_casting_2_1 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 1)
            qty_casting_2_2 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 2)
            qty_casting_2_3 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 3)
            qty_casting_2_4 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 4)
            qty_casting_2_5 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 5)
            qty_casting_2_6 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 6)
            qty_casting_2_7 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 7)
            qty_casting_2_8 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 8)
            qty_casting_2_9 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 9)
            qty_casting_2_10 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 10)
            qty_casting_2_11 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 11)
            qty_casting_2_12 = self.qty_casting(cr, uid, date_from, date_to, 2, type, 12)
            
            qty_casting_3_1 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 1)
            qty_casting_3_2 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 2)
            qty_casting_3_3 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 3)
            qty_casting_3_4 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 4)
            qty_casting_3_5 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 5)
            qty_casting_3_6 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 6)
            qty_casting_3_7 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 7)
            qty_casting_3_8 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 8)
            qty_casting_3_9 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 9)
            qty_casting_3_10 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 10)
            qty_casting_3_11 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 11)
            qty_casting_3_12 = self.qty_casting(cr, uid, date_from, date_to, 3, type, 12)
            
            qty_casting_4_1 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 1)
            qty_casting_4_2 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 2)
            qty_casting_4_3 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 3)
            qty_casting_4_4 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 4)
            qty_casting_4_5 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 5)
            qty_casting_4_6 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 6)
            qty_casting_4_7 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 7)
            qty_casting_4_8 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 8)
            qty_casting_4_9 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 9)
            qty_casting_4_10 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 10)
            qty_casting_4_11 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 11)
            qty_casting_4_12 = self.qty_casting(cr, uid, date_from, date_to, 4, type, 12)
            
            qty_assembling_easy_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 1)
            qty_assembling_easy_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 2)
            qty_assembling_easy_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 3)
            qty_assembling_easy_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 4)
            qty_assembling_easy_5 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 5)
            qty_assembling_easy_6 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 6)
            qty_assembling_easy_7 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 7)
            qty_assembling_easy_8 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 8)
            qty_assembling_easy_9 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 9)
            qty_assembling_easy_10 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 10)
            qty_assembling_easy_11 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 11)
            qty_assembling_easy_12 = self.qty_assembling(cr, uid, date_from, date_to, 'Easy', type, 12)
            
            qty_assembling_medium_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 1)
            qty_assembling_medium_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 2)
            qty_assembling_medium_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 3)
            qty_assembling_medium_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 4)
            qty_assembling_medium_5 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 5)
            qty_assembling_medium_6 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 6)
            qty_assembling_medium_7 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 7)
            qty_assembling_medium_8 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 8)
            qty_assembling_medium_9 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 9)
            qty_assembling_medium_10 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 10)
            qty_assembling_medium_11 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 11)
            qty_assembling_medium_12 = self.qty_assembling(cr, uid, date_from, date_to, 'Medium', type, 12)
            
            qty_assembling_hard_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 1)
            qty_assembling_hard_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 2)
            qty_assembling_hard_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 3)
            qty_assembling_hard_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 4)
            qty_assembling_hard_5 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 5)
            qty_assembling_hard_6 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 6)
            qty_assembling_hard_7 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 7)
            qty_assembling_hard_8 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 8)
            qty_assembling_hard_9 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 9)
            qty_assembling_hard_10 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 10)
            qty_assembling_hard_11 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 11)
            qty_assembling_hard_12 = self.qty_assembling(cr, uid, date_from, date_to, 'Hard', type, 12)
            
            qty_assembling_very_hard_1 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 1)
            qty_assembling_very_hard_2 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 2)
            qty_assembling_very_hard_3 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 3)
            qty_assembling_very_hard_4 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 4)
            qty_assembling_very_hard_5 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 5)
            qty_assembling_very_hard_6 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 6)
            qty_assembling_very_hard_7 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 7)
            qty_assembling_very_hard_8 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 8)
            qty_assembling_very_hard_9 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 9)
            qty_assembling_very_hard_10 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 10)
            qty_assembling_very_hard_11 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 11)
            qty_assembling_very_hard_12 = self.qty_assembling(cr, uid, date_from, date_to, 'Very Hard', type, 12)
            
            qty_setting_i_1 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 1)
            qty_setting_i_2 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 2)
            qty_setting_i_3 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 3)
            qty_setting_i_4 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 4)
            qty_setting_i_5 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 5)
            qty_setting_i_6 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 6)
            qty_setting_i_7 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 7)
            qty_setting_i_8 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 8)
            qty_setting_i_9 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 9)
            qty_setting_i_10 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 10)
            qty_setting_i_11 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 11)
            qty_setting_i_12 = self.qty_setting(cr, uid, date_from, date_to, 'I', type, 12)
            
            qty_setting_ii_1 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 1)
            qty_setting_ii_2 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 2)
            qty_setting_ii_3 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 3)
            qty_setting_ii_4 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 4)
            qty_setting_ii_5 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 5)
            qty_setting_ii_6 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 6)
            qty_setting_ii_7 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 7)
            qty_setting_ii_8 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 8)
            qty_setting_ii_9 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 9)
            qty_setting_ii_10 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 10)
            qty_setting_ii_11 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 11)
            qty_setting_ii_12 = self.qty_setting(cr, uid, date_from, date_to, 'II', type, 12)
            
            qty_setting_iii_1 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 1)
            qty_setting_iii_2 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 2)
            qty_setting_iii_3 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 3)
            qty_setting_iii_4 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 4)
            qty_setting_iii_5 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 5)
            qty_setting_iii_6 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 6)
            qty_setting_iii_7 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 7)
            qty_setting_iii_8 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 8)
            qty_setting_iii_9 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 9)
            qty_setting_iii_10 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 10)
            qty_setting_iii_11 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 11)
            qty_setting_iii_12 = self.qty_setting(cr, uid, date_from, date_to, 'III', type, 12)
            
            qty_setting_iv_1 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 1)
            qty_setting_iv_2 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 2)
            qty_setting_iv_3 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 3)
            qty_setting_iv_4 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 4)
            qty_setting_iv_5 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 5)
            qty_setting_iv_6 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 6)
            qty_setting_iv_7 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 7)
            qty_setting_iv_8 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 8)
            qty_setting_iv_9 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 9)
            qty_setting_iv_10 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 10)
            qty_setting_iv_11 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 11)
            qty_setting_iv_12 = self.qty_setting(cr, uid, date_from, date_to, 'IV', type, 12)
            
            qty_setting_v_1 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 1)
            qty_setting_v_2 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 2)
            qty_setting_v_3 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 3)
            qty_setting_v_4 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 4)
            qty_setting_v_5 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 5)
            qty_setting_v_6 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 6)
            qty_setting_v_7 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 7)
            qty_setting_v_8 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 8)
            qty_setting_v_9 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 9)
            qty_setting_v_10 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 10)
            qty_setting_v_11 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 11)
            qty_setting_v_12 = self.qty_setting(cr, uid, date_from, date_to, 'V', type, 12)
            
            qty_setting_vi_1 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 1)
            qty_setting_vi_2 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 2)
            qty_setting_vi_3 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 3)
            qty_setting_vi_4 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 4)
            qty_setting_vi_5 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 5)
            qty_setting_vi_6 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 6)
            qty_setting_vi_7 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 7)
            qty_setting_vi_8 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 8)
            qty_setting_vi_9 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 9)
            qty_setting_vi_10 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 10)
            qty_setting_vi_11 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 11)
            qty_setting_vi_12 = self.qty_setting(cr, uid, date_from, date_to, 'VI', type, 12)
            
            qty_setting_vii_1 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 1)
            qty_setting_vii_2 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 2)
            qty_setting_vii_3 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 3)
            qty_setting_vii_4 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 4)
            qty_setting_vii_5 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 5)
            qty_setting_vii_6 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 6)
            qty_setting_vii_7 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 7)
            qty_setting_vii_8 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 8)
            qty_setting_vii_9 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 9)
            qty_setting_vii_10 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 10)
            qty_setting_vii_11 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 11)
            qty_setting_vii_12 = self.qty_setting(cr, uid, date_from, date_to, 'VII', type, 12)
            
            qty_setting_viii_1 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 1)
            qty_setting_viii_2 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 2)
            qty_setting_viii_3 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 3)
            qty_setting_viii_4 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 4)
            qty_setting_viii_5 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 5)
            qty_setting_viii_6 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 6)
            qty_setting_viii_7 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 7)
            qty_setting_viii_8 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 8)
            qty_setting_viii_9 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 9)
            qty_setting_viii_10 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 10)
            qty_setting_viii_11 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 11)
            qty_setting_viii_12 = self.qty_setting(cr, uid, date_from, date_to, 'VIII', type, 12)
            
            qty_setting_ix_1 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 1)
            qty_setting_ix_2 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 2)
            qty_setting_ix_3 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 3)
            qty_setting_ix_4 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 4)
            qty_setting_ix_5 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 5)
            qty_setting_ix_6 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 6)
            qty_setting_ix_7 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 7)
            qty_setting_ix_8 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 8)
            qty_setting_ix_9 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 9)
            qty_setting_ix_10 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 10)
            qty_setting_ix_11 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 11)
            qty_setting_ix_12 = self.qty_setting(cr, uid, date_from, date_to, 'IX', type, 12)
                      
            
            arr = {
                      'coeff_3d_1': self._3d_times(cr, uid, '=', 1),
                      'qty_3d_1_1': qty_3d_1_1,
                      'qty_3d_1_2': qty_3d_1_2,
                      'qty_3d_1_3': qty_3d_1_3,
                      'qty_3d_1_4': qty_3d_1_4,
                      'qty_3d_1_5': qty_3d_1_5,
                      'qty_3d_1_6': qty_3d_1_6,
                      'qty_3d_1_7': qty_3d_1_7,
                      'qty_3d_1_8': qty_3d_1_8,
                      'qty_3d_1_9': qty_3d_1_9,
                      'qty_3d_1_10': qty_3d_1_10,
                      'qty_3d_1_11': qty_3d_1_11,
                      'qty_3d_1_12': qty_3d_1_12,
                      'qty_3d_1_total': qty_3d_1_1 + qty_3d_1_2 + qty_3d_1_3 + qty_3d_1_4 + qty_3d_1_5 + qty_3d_1_6 + qty_3d_1_7 + qty_3d_1_8 + qty_3d_1_9 + qty_3d_1_10 + qty_3d_1_11 + qty_3d_1_12,
                      'emp_3d_1': self._3d_employee_times(cr, uid, date_from, date_to, '=', 1),
                      'target_3d_1': 0,
                      
                      'coeff_3d_2': self._3d_times(cr, uid, '=', 2),
                      'qty_3d_2_1': qty_3d_2_1,
                      'qty_3d_2_2': qty_3d_2_2,
                      'qty_3d_2_3': qty_3d_2_3,
                      'qty_3d_2_4': qty_3d_2_4,
                      'qty_3d_2_5': qty_3d_2_5,
                      'qty_3d_2_6': qty_3d_2_6,
                      'qty_3d_2_7': qty_3d_2_7,
                      'qty_3d_2_8': qty_3d_2_8,
                      'qty_3d_2_9': qty_3d_2_9,
                      'qty_3d_2_10': qty_3d_2_10,
                      'qty_3d_2_11': qty_3d_2_11,
                      'qty_3d_2_12': qty_3d_2_12,
                      'qty_3d_2_total': qty_3d_2_1 + qty_3d_2_2 + qty_3d_2_3 + qty_3d_2_4 + qty_3d_2_5 + qty_3d_2_6 + qty_3d_2_7 + qty_3d_2_8 + qty_3d_2_9 + qty_3d_2_10 + qty_3d_2_11 + qty_3d_2_12,
                      'emp_3d_2': self._3d_employee_times(cr, uid, date_from, date_to, '=', 2),
                      'target_3d_2': 0,
                      
                      'coeff_3d_3': self._3d_times(cr, uid, '=', 3),
                      'qty_3d_3_1': qty_3d_3_1,
                      'qty_3d_3_2': qty_3d_3_2,
                      'qty_3d_3_3': qty_3d_3_3,
                      'qty_3d_3_4': qty_3d_3_4,
                      'qty_3d_3_5': qty_3d_3_5,
                      'qty_3d_3_6': qty_3d_3_6,
                      'qty_3d_3_7': qty_3d_3_7,
                      'qty_3d_3_8': qty_3d_3_8,
                      'qty_3d_3_9': qty_3d_3_9,
                      'qty_3d_3_10': qty_3d_3_10,
                      'qty_3d_3_11': qty_3d_3_11,
                      'qty_3d_3_12': qty_3d_3_12,
                      'qty_3d_3_total': qty_3d_3_1 + qty_3d_3_2 + qty_3d_3_3 + qty_3d_3_4 + qty_3d_3_5 + qty_3d_3_6 + qty_3d_3_7 + qty_3d_3_8 + qty_3d_3_9 + qty_3d_3_10 + qty_3d_3_11 + qty_3d_3_12,
                      'emp_3d_3': self._3d_employee_times(cr, uid, date_from, date_to, '=', 3),
                      'target_3d_3': 0,
                      
                      'coeff_3d_4': self._3d_times(cr, uid, '>=', 4),
                      'qty_3d_4_1': qty_3d_4_1,
                      'qty_3d_4_2': qty_3d_4_2,
                      'qty_3d_4_3': qty_3d_4_3,
                      'qty_3d_4_4': qty_3d_4_4,
                      'qty_3d_4_5': qty_3d_4_5,
                      'qty_3d_4_6': qty_3d_4_6,
                      'qty_3d_4_7': qty_3d_4_7,
                      'qty_3d_4_8': qty_3d_4_8,
                      'qty_3d_4_9': qty_3d_4_9,
                      'qty_3d_4_10': qty_3d_4_10,
                      'qty_3d_4_11': qty_3d_4_11,
                      'qty_3d_4_12': qty_3d_4_12,
                      'qty_3d_4_total': qty_3d_4_1 + qty_3d_4_2 + qty_3d_4_3 + qty_3d_4_4 + qty_3d_4_5 + qty_3d_4_6 + qty_3d_4_7 + qty_3d_4_8 + qty_3d_4_9 + qty_3d_4_10 + qty_3d_4_11 + qty_3d_4_12,
                      'emp_3d_4': self._3d_employee_times(cr, uid, date_from, date_to, '>=', 4),
                      'target_3d_4': 0,
                      
                      'coeff_3d_easy': self._3d_level(cr, uid, 'Easy'),
                      'qty_3d_easy_1':  qty_3d_easy_1,
                      'qty_3d_easy_2':  qty_3d_easy_2,
                      'qty_3d_easy_3':  qty_3d_easy_2,
                      'qty_3d_easy_4':  qty_3d_easy_4,
                      'qty_3d_easy_5':  qty_3d_easy_5,
                      'qty_3d_easy_6':  qty_3d_easy_6,
                      'qty_3d_easy_7':  qty_3d_easy_7,
                      'qty_3d_easy_8':  qty_3d_easy_8,
                      'qty_3d_easy_9':  qty_3d_easy_9,
                      'qty_3d_easy_10':  qty_3d_easy_10,
                      'qty_3d_easy_11':  qty_3d_easy_11,
                      'qty_3d_easy_12':  qty_3d_easy_12,
                      'qty_3d_easy_total':  qty_3d_easy_1 + qty_3d_easy_2 + qty_3d_easy_3 + qty_3d_easy_4 + qty_3d_easy_5 + qty_3d_easy_6 + qty_3d_easy_7 + qty_3d_easy_8 + qty_3d_easy_9 + qty_3d_easy_10 + qty_3d_easy_11 + qty_3d_easy_12,
                      'emp_3d_easy': self._3d_employee_level(cr, uid, date_from, date_to, 'Easy'),
                      'target_3d_easy': self._3d_target(cr, uid, 'Easy'),
                      
                      'coeff_3d_medium': self._3d_level(cr, uid, 'Medium'),
                      'qty_3d_medium_1': qty_3d_medium_1,
                      'qty_3d_medium_2': qty_3d_medium_2,
                      'qty_3d_medium_3': qty_3d_medium_3,
                      'qty_3d_medium_4': qty_3d_medium_4,
                      'qty_3d_medium_5': qty_3d_medium_5,
                      'qty_3d_medium_6': qty_3d_medium_6,
                      'qty_3d_medium_7': qty_3d_medium_7,
                      'qty_3d_medium_8': qty_3d_medium_8,
                      'qty_3d_medium_9': qty_3d_medium_9,
                      'qty_3d_medium_10': qty_3d_medium_10,
                      'qty_3d_medium_11': qty_3d_medium_11,
                      'qty_3d_medium_12': qty_3d_medium_12,
                      'qty_3d_medium_total': qty_3d_medium_1 + qty_3d_medium_2 + qty_3d_medium_3 + qty_3d_medium_4 + qty_3d_medium_5 + qty_3d_medium_6 + qty_3d_medium_7 + qty_3d_medium_8 + qty_3d_medium_9 + qty_3d_medium_10 + qty_3d_medium_11 + qty_3d_medium_12,
                      'emp_3d_medium': self._3d_employee_level(cr, uid, date_from, date_to, 'Medium'),
                      'target_3d_medium': self._3d_target(cr, uid, 'Medium'),
                      
                      'coeff_3d_medium_hard': self._3d_level(cr, uid, 'Medium - Hard'),
                      'qty_3d_medium_hard_1': qty_3d_medium_hard_1,
                      'qty_3d_medium_hard_2': qty_3d_medium_hard_2,
                      'qty_3d_medium_hard_3': qty_3d_medium_hard_3,
                      'qty_3d_medium_hard_4': qty_3d_medium_hard_4,
                      'qty_3d_medium_hard_5': qty_3d_medium_hard_5,
                      'qty_3d_medium_hard_6': qty_3d_medium_hard_6,
                      'qty_3d_medium_hard_7': qty_3d_medium_hard_7,
                      'qty_3d_medium_hard_8': qty_3d_medium_hard_8,
                      'qty_3d_medium_hard_9': qty_3d_medium_hard_9,
                      'qty_3d_medium_hard_10': qty_3d_medium_hard_10,
                      'qty_3d_medium_hard_11': qty_3d_medium_hard_11,
                      'qty_3d_medium_hard_12': qty_3d_medium_hard_12,
                      'qty_3d_medium_hard_total': qty_3d_medium_hard_1 + qty_3d_medium_hard_2 + qty_3d_medium_hard_3 + qty_3d_medium_hard_4 + qty_3d_medium_hard_5 + qty_3d_medium_hard_6 + qty_3d_medium_hard_7 + qty_3d_medium_hard_8 + qty_3d_medium_hard_9 + qty_3d_medium_hard_10 + qty_3d_medium_hard_11 + qty_3d_medium_hard_12,
                      'emp_3d_medium_hard': self._3d_employee_level(cr, uid, date_from, date_to, 'Medium - Hard'),
                      'target_3d_medium_hard': self._3d_target(cr, uid, 'Medium - Hard'),
                      
                      'coeff_3d_hard': self._3d_level(cr, uid, 'Hard'),
                      'qty_3d_hard_1': qty_3d_hard_1,
                      'qty_3d_hard_2': qty_3d_hard_2,
                      'qty_3d_hard_3': qty_3d_hard_3,
                      'qty_3d_hard_4': qty_3d_hard_4,
                      'qty_3d_hard_5': qty_3d_hard_5,
                      'qty_3d_hard_6': qty_3d_hard_6,
                      'qty_3d_hard_7': qty_3d_hard_7,
                      'qty_3d_hard_8': qty_3d_hard_8,
                      'qty_3d_hard_9': qty_3d_hard_9,
                      'qty_3d_hard_10': qty_3d_hard_10,
                      'qty_3d_hard_11': qty_3d_hard_11,
                      'qty_3d_hard_12': qty_3d_hard_12,
                      'qty_3d_hard_total': qty_3d_hard_1 + qty_3d_hard_2 + qty_3d_hard_3 + qty_3d_hard_4 + qty_3d_hard_5 + qty_3d_hard_6 + qty_3d_hard_7 + qty_3d_hard_8 + qty_3d_hard_9 + qty_3d_hard_10 + qty_3d_hard_11 + qty_3d_hard_12,
                      'emp_3d_hard': self._3d_employee_level(cr, uid, date_from, date_to, 'Hard'),
                      'target_3d_hard': self._3d_target(cr, uid, 'Hard'),
                      
                      'coeff_3d_very_hard': self._3d_level(cr, uid, 'Very Hard'),
                      'qty_3d_very_hard_1': qty_3d_very_hard_1,
                      'qty_3d_very_hard_2': qty_3d_very_hard_2,
                      'qty_3d_very_hard_3': qty_3d_very_hard_3,
                      'qty_3d_very_hard_4': qty_3d_very_hard_4,
                      'qty_3d_very_hard_5': qty_3d_very_hard_5,
                      'qty_3d_very_hard_6': qty_3d_very_hard_6,
                      'qty_3d_very_hard_7': qty_3d_very_hard_7,
                      'qty_3d_very_hard_8': qty_3d_very_hard_8,
                      'qty_3d_very_hard_9': qty_3d_very_hard_9,
                      'qty_3d_very_hard_10': qty_3d_very_hard_10,
                      'qty_3d_very_hard_11': qty_3d_very_hard_11,
                      'qty_3d_very_hard_12': qty_3d_very_hard_12,
                      'qty_3d_very_hard_total': qty_3d_very_hard_1 + qty_3d_very_hard_2 + qty_3d_very_hard_3 + qty_3d_very_hard_4 + qty_3d_very_hard_5 + qty_3d_very_hard_6 + qty_3d_very_hard_7 + qty_3d_very_hard_8 + qty_3d_very_hard_9 + qty_3d_very_hard_10 + qty_3d_very_hard_11 + qty_3d_very_hard_12,
                      'emp_3d_very_hard': self._3d_employee_level(cr, uid, date_from, date_to, 'Very Hard'),
                      'target_3d_very_hard': self._3d_target(cr, uid, 'Very Hard'),
                      
                      
                      'coeff_casting_1' : self.casting(cr, uid, '=', 1),
                      'qty_casting_1_1': qty_casting_1_1,
                      'qty_casting_1_2': qty_casting_1_2,
                      'qty_casting_1_3': qty_casting_1_3,
                      'qty_casting_1_4': qty_casting_1_4,
                      'qty_casting_1_5': qty_casting_1_5,
                      'qty_casting_1_6': qty_casting_1_6,
                      'qty_casting_1_7': qty_casting_1_7,
                      'qty_casting_1_8': qty_casting_1_8,
                      'qty_casting_1_9': qty_casting_1_9,
                      'qty_casting_1_10': qty_casting_1_10,
                      'qty_casting_1_11': qty_casting_1_11,
                      'qty_casting_1_12': qty_casting_1_12,
                      'qty_casting_1_total': qty_casting_1_1 + qty_casting_1_2 + qty_casting_1_3 + qty_casting_1_4 + qty_casting_1_5 + qty_casting_1_6 + qty_casting_1_7 + qty_casting_1_8 + qty_casting_1_9 + qty_casting_1_10 + qty_casting_1_11 + qty_casting_1_12,
                      'emp_casting_1': self.casting_employee(cr, uid, date_from, date_to, '=', 1),
                      'target_casting_1': 0,
                      
                      'coeff_casting_2' : self.casting(cr, uid, '=', 2),
                      'qty_casting_2_1': qty_casting_2_1,
                      'qty_casting_2_2': qty_casting_2_2,
                      'qty_casting_2_3': qty_casting_2_3,
                      'qty_casting_2_4': qty_casting_2_4,
                      'qty_casting_2_5': qty_casting_2_5,
                      'qty_casting_2_6': qty_casting_2_6,
                      'qty_casting_2_7': qty_casting_2_7,
                      'qty_casting_2_8': qty_casting_2_8,
                      'qty_casting_2_9': qty_casting_2_9,
                      'qty_casting_2_10': qty_casting_2_10,
                      'qty_casting_2_11': qty_casting_2_11,
                      'qty_casting_2_12': qty_casting_2_12,
                      'qty_casting_2_total': qty_casting_2_1 + qty_casting_2_2 + qty_casting_2_3 + qty_casting_2_4 + qty_casting_2_5 + qty_casting_2_6 + qty_casting_2_7 + qty_casting_2_8 +qty_casting_2_9 + qty_casting_2_10 + qty_casting_2_11 + qty_casting_2_12,
                      'emp_casting_2': self.casting_employee(cr, uid, date_from, date_to, '=', 2),
                      'target_casting_2': 0,
                      
                      'coeff_casting_3' : self.casting(cr, uid, '=', 3),
                      'qty_casting_3_1': qty_casting_3_1,
                      'qty_casting_3_2': qty_casting_3_2,
                      'qty_casting_3_3': qty_casting_3_3,
                      'qty_casting_3_4':  qty_casting_3_4,
                      'qty_casting_3_5':  qty_casting_3_5,
                      'qty_casting_3_6':  qty_casting_3_6,
                      'qty_casting_3_7':  qty_casting_3_7,
                      'qty_casting_3_8':  qty_casting_3_8,
                      'qty_casting_3_9':  qty_casting_3_9,
                      'qty_casting_3_10':  qty_casting_3_10,
                      'qty_casting_3_11':  qty_casting_3_11,
                      'qty_casting_3_12':  qty_casting_3_12,
                      'qty_casting_3_total':  qty_casting_3_1 + qty_casting_3_2 + qty_casting_3_3 + qty_casting_3_4 + qty_casting_3_5 + qty_casting_3_6 + qty_casting_3_7 + qty_casting_3_8 + qty_casting_3_9 + qty_casting_3_10 + qty_casting_3_11 + qty_casting_3_12,
                      'emp_casting_3': self.casting_employee(cr, uid, date_from, date_to, '=', 3),
                      'target_casting_3': 0,
                      
                      'coeff_casting_4' : self.casting(cr, uid, '>=', 4),
                      'qty_casting_4_1':  qty_casting_4_1,
                      'qty_casting_4_2': qty_casting_4_2,
                      'qty_casting_4_3': qty_casting_4_3,
                      'qty_casting_4_4': qty_casting_4_4,
                      'qty_casting_4_5': qty_casting_4_5,
                      'qty_casting_4_6': qty_casting_4_6,
                      'qty_casting_4_7': qty_casting_4_7,
                      'qty_casting_4_8': qty_casting_4_8,
                      'qty_casting_4_9': qty_casting_4_9,
                      'qty_casting_4_10': qty_casting_4_10,
                      'qty_casting_4_11': qty_casting_4_11,
                      'qty_casting_4_12': qty_casting_4_12,
                      'qty_casting_4_total': qty_casting_4_1 + qty_casting_4_2 + qty_casting_4_3 + qty_casting_4_4 + qty_casting_4_5 + qty_casting_4_6 + qty_casting_4_7 + qty_casting_4_8 + qty_casting_4_9 + qty_casting_4_10 + qty_casting_4_11 + qty_casting_4_12,
                      'emp_casting_4': self.casting_employee(cr, uid, date_from, date_to, '=', 4),
                      'target_casting_4': 0,
                      
                      
                      'coeff_assembling_easy': self.assembling(cr, uid, 'Easy'),
                      'qty_assembling_easy_1': qty_assembling_easy_1,
                      'qty_assembling_easy_2': qty_assembling_easy_2,
                      'qty_assembling_easy_3': qty_assembling_easy_3,
                      'qty_assembling_easy_4': qty_assembling_easy_4,
                      'qty_assembling_easy_5': qty_assembling_easy_5,
                      'qty_assembling_easy_6': qty_assembling_easy_6,
                      'qty_assembling_easy_7': qty_assembling_easy_7,
                      'qty_assembling_easy_8': qty_assembling_easy_8,
                      'qty_assembling_easy_9': qty_assembling_easy_9,
                      'qty_assembling_easy_10': qty_assembling_easy_10,
                      'qty_assembling_easy_11': qty_assembling_easy_11,
                      'qty_assembling_easy_12': qty_assembling_easy_12,
                      'qty_assembling_easy_total': qty_assembling_easy_1 + qty_assembling_easy_2 + qty_assembling_easy_3 + qty_assembling_easy_4 + qty_assembling_easy_5 + qty_assembling_easy_6 + qty_assembling_easy_7 + qty_assembling_easy_8 + qty_assembling_easy_9 + qty_assembling_easy_10 + qty_assembling_easy_11 + qty_assembling_easy_12,
                      'emp_assembling_easy'  : self.assembling_employee(cr, uid, date_from, date_to, 'Easy'),
                      'target_assembling_easy': self.target_assembling(cr, uid, 'Easy'),
                      
                      'coeff_assembling_medium': self.assembling(cr, uid, 'Medium'),
                      'qty_assembling_medium_1': qty_assembling_medium_1,
                      'qty_assembling_medium_2': qty_assembling_medium_2,
                      'qty_assembling_medium_3': qty_assembling_medium_3,
                      'qty_assembling_medium_4': qty_assembling_medium_4,
                      'qty_assembling_medium_5': qty_assembling_medium_5,
                      'qty_assembling_medium_6': qty_assembling_medium_6,
                      'qty_assembling_medium_7': qty_assembling_medium_7,
                      'qty_assembling_medium_8': qty_assembling_medium_8,
                      'qty_assembling_medium_9': qty_assembling_medium_9,
                      'qty_assembling_medium_10': qty_assembling_medium_10,
                      'qty_assembling_medium_11': qty_assembling_medium_11,
                      'qty_assembling_medium_12': qty_assembling_medium_12,
                      'qty_assembling_medium_total': qty_assembling_medium_1 + qty_assembling_medium_2 + qty_assembling_medium_3 + qty_assembling_medium_4 + qty_assembling_medium_5 + qty_assembling_medium_6 + qty_assembling_medium_7 + qty_assembling_medium_8 + qty_assembling_medium_8 + qty_assembling_medium_10 + qty_assembling_medium_11 + qty_assembling_medium_12,
                      'emp_assembling_medium'  : self.assembling_employee(cr, uid, date_from, date_to, 'Medium'),
                      'target_assembling_medium': self.target_assembling(cr, uid, 'Medium'),
                      
                      'coeff_assembling_hard': self.assembling(cr, uid, 'Hard'),
                      'qty_assembling_hard_1': qty_assembling_hard_1,
                      'qty_assembling_hard_2': qty_assembling_hard_2,
                      'qty_assembling_hard_3': qty_assembling_hard_3,
                      'qty_assembling_hard_4': qty_assembling_hard_4,
                      'qty_assembling_hard_5': qty_assembling_hard_5,
                      'qty_assembling_hard_6': qty_assembling_hard_6,
                      'qty_assembling_hard_7': qty_assembling_hard_7,
                      'qty_assembling_hard_8': qty_assembling_hard_8,
                      'qty_assembling_hard_9': qty_assembling_hard_9,
                      'qty_assembling_hard_10': qty_assembling_hard_10,
                      'qty_assembling_hard_11': qty_assembling_hard_11,
                      'qty_assembling_hard_12': qty_assembling_hard_12,
                      'qty_assembling_hard_total': qty_assembling_hard_1 + qty_assembling_hard_2 + qty_assembling_hard_3 + qty_assembling_hard_4 + qty_assembling_hard_5 + qty_assembling_hard_6 + qty_assembling_hard_7 + qty_assembling_hard_8 + qty_assembling_hard_9 + qty_assembling_hard_10 + qty_assembling_hard_11 + qty_assembling_hard_12,
                      'emp_assembling_hard'  : self.assembling_employee(cr, uid, date_from, date_to, 'Hard'),
                      'target_assembling_hard': self.target_assembling(cr, uid, 'Hard'),
                      
                      'coeff_assembling_very_hard': self.assembling(cr, uid, 'Very Hard'),
                      'qty_assembling_very_hard_1': qty_assembling_very_hard_1,
                      'qty_assembling_very_hard_2': qty_assembling_very_hard_2,
                      'qty_assembling_very_hard_3': qty_assembling_very_hard_3,
                      'qty_assembling_very_hard_4': qty_assembling_very_hard_4,
                      'qty_assembling_very_hard_5': qty_assembling_very_hard_5,
                      'qty_assembling_very_hard_6': qty_assembling_very_hard_6,
                      'qty_assembling_very_hard_7': qty_assembling_very_hard_7,
                      'qty_assembling_very_hard_8': qty_assembling_very_hard_8,
                      'qty_assembling_very_hard_9': qty_assembling_very_hard_9,
                      'qty_assembling_very_hard_10': qty_assembling_very_hard_10,
                      'qty_assembling_very_hard_11': qty_assembling_very_hard_11,
                      'qty_assembling_very_hard_12': qty_assembling_very_hard_12,
                      'qty_assembling_very_hard_total': qty_assembling_very_hard_1 + qty_assembling_very_hard_2 + qty_assembling_very_hard_3 + qty_assembling_very_hard_4 + qty_assembling_very_hard_5 + qty_assembling_very_hard_6 + qty_assembling_very_hard_7 + qty_assembling_very_hard_8 + qty_assembling_very_hard_9 + qty_assembling_very_hard_10 + qty_assembling_very_hard_11 + qty_assembling_very_hard_12,
                      'emp_assembling_very_hard'  : self.assembling_employee(cr, uid, date_from, date_to, 'Very Hard'),
                      'target_assembling_very_hard': self.target_assembling(cr, uid, 'Very Hard'),
                      
                      
                      'coeff_setting_i': self.setting(cr, uid, 'I'),
                      'qty_setting_i_1': qty_setting_i_1,
                      'qty_setting_i_2': qty_setting_i_2,
                      'qty_setting_i_3': qty_setting_i_3,
                      'qty_setting_i_4': qty_setting_i_4,
                      'qty_setting_i_5': qty_setting_i_5,
                      'qty_setting_i_6': qty_setting_i_6,
                      'qty_setting_i_7': qty_setting_i_7,
                      'qty_setting_i_8': qty_setting_i_8,
                      'qty_setting_i_9': qty_setting_i_9,
                      'qty_setting_i_10': qty_setting_i_10,
                      'qty_setting_i_11': qty_setting_i_11,
                      'qty_setting_i_12': qty_setting_i_12,
                      'qty_setting_i_total': qty_setting_i_1 + qty_setting_i_2 + qty_setting_i_3 + qty_setting_i_4 + qty_setting_i_5 + qty_setting_i_6 + qty_setting_i_7 + qty_setting_i_8 + qty_setting_i_9 + qty_setting_i_10 + qty_setting_i_11 + qty_setting_i_12,
                      'emp_setting_i': self.setting_employee(cr, uid, date_from, date_to, 'I'),
                      'target_setting_i': self.target_setting(cr, uid, 'I'),
                      
                      'coeff_setting_ii': self.setting(cr, uid, 'II'),
                      'qty_setting_ii_1': qty_setting_ii_1,
                      'qty_setting_ii_2': qty_setting_ii_2,
                      'qty_setting_ii_3': qty_setting_ii_3,
                      'qty_setting_ii_4': qty_setting_ii_4,
                      'qty_setting_ii_5': qty_setting_ii_5,
                      'qty_setting_ii_6': qty_setting_ii_6,
                      'qty_setting_ii_7': qty_setting_ii_7,
                      'qty_setting_ii_8': qty_setting_ii_8,
                      'qty_setting_ii_9': qty_setting_ii_9,
                      'qty_setting_ii_10': qty_setting_ii_10,
                      'qty_setting_ii_11': qty_setting_ii_11,
                      'qty_setting_ii_12': qty_setting_ii_12,
                      'qty_setting_ii_total': qty_setting_ii_1 + qty_setting_ii_2 + qty_setting_ii_3 + qty_setting_ii_4 + qty_setting_ii_5 + qty_setting_ii_6 + qty_setting_ii_7 + qty_setting_ii_8 + qty_setting_ii_9 + qty_setting_ii_10 + qty_setting_ii_11 + qty_setting_ii_12,
                      'emp_setting_ii': self.setting_employee(cr, uid, date_from, date_to, 'II'),
                      'target_setting_ii': self.target_setting(cr, uid, 'II'),
                      
                      'coeff_setting_iii': self.setting(cr, uid, 'III'),
                      'qty_setting_iii_1': qty_setting_iii_1,
                      'qty_setting_iii_2': qty_setting_iii_2,
                      'qty_setting_iii_3': qty_setting_iii_3,
                      'qty_setting_iii_4': qty_setting_iii_4,
                      'qty_setting_iii_5': qty_setting_iii_5,
                      'qty_setting_iii_6': qty_setting_iii_6,
                      'qty_setting_iii_7': qty_setting_iii_7,
                      'qty_setting_iii_8': qty_setting_iii_8,
                      'qty_setting_iii_9': qty_setting_iii_9,
                      'qty_setting_iii_10': qty_setting_iii_10,
                      'qty_setting_iii_11': qty_setting_iii_11,
                      'qty_setting_iii_12': qty_setting_iii_12,
                      'qty_setting_iii_total': qty_setting_iii_1 + qty_setting_iii_2 + qty_setting_iii_3 + qty_setting_iii_4 + qty_setting_iii_5 + qty_setting_iii_6 + qty_setting_iii_7 + qty_setting_iii_8 + qty_setting_iii_9 + qty_setting_iii_10 + qty_setting_iii_11 + qty_setting_iii_12,
                      'emp_setting_iii': self.setting_employee(cr, uid, date_from, date_to, 'III'),
                      'target_setting_iii': self.target_setting(cr, uid, 'III'),
                      
                      'coeff_setting_iv': self.setting(cr, uid, 'IV'),
                      'qty_setting_iv_1': qty_setting_iv_1,
                      'qty_setting_iv_2': qty_setting_iv_2,
                      'qty_setting_iv_3': qty_setting_iv_3,
                      'qty_setting_iv_4': qty_setting_iv_4,
                      'qty_setting_iv_5': qty_setting_iv_5,
                      'qty_setting_iv_6': qty_setting_iv_6,
                      'qty_setting_iv_7': qty_setting_iv_7,
                      'qty_setting_iv_8': qty_setting_iv_8,
                      'qty_setting_iv_9': qty_setting_iv_9,
                      'qty_setting_iv_10': qty_setting_iv_10,
                      'qty_setting_iv_11': qty_setting_iv_11,
                      'qty_setting_iv_12': qty_setting_iv_12,
                      'qty_setting_iv_total': qty_setting_iv_1 + qty_setting_iv_2 + qty_setting_iv_3 + qty_setting_iv_4 + qty_setting_iv_5 + qty_setting_iv_6 + qty_setting_iv_7 + qty_setting_iv_8 + qty_setting_iv_9 + qty_setting_iv_10 + qty_setting_iv_11 + qty_setting_iv_12,
                      'emp_setting_iv': self.setting_employee(cr, uid, date_from, date_to, 'IV'),
                      'target_setting_iv': self.target_setting(cr, uid, 'IV'),
                      
                      'coeff_setting_v': self.setting(cr, uid, 'V'),
                      'qty_setting_v_1': qty_setting_v_1,
                      'qty_setting_v_2': qty_setting_v_2,
                      'qty_setting_v_3': qty_setting_v_3,
                      'qty_setting_v_4': qty_setting_v_4,
                      'qty_setting_v_5': qty_setting_v_5,
                      'qty_setting_v_6': qty_setting_v_6,
                      'qty_setting_v_7': qty_setting_v_7,
                      'qty_setting_v_8': qty_setting_v_8,
                      'qty_setting_v_9': qty_setting_v_9,
                      'qty_setting_v_10': qty_setting_v_10,
                      'qty_setting_v_11': qty_setting_v_11,
                      'qty_setting_v_12': qty_setting_v_12,
                      'qty_setting_v_total': qty_setting_v_1 + qty_setting_v_2 + qty_setting_v_3 + qty_setting_v_4 + qty_setting_v_5 + qty_setting_v_6 + qty_setting_v_7 + qty_setting_v_8 + qty_setting_v_9 + qty_setting_v_10 + qty_setting_v_11 + qty_setting_v_12,
                      'emp_setting_v': self.setting_employee(cr, uid, date_from, date_to, 'V'),
                      'target_setting_v': self.target_setting(cr, uid, 'V'),
                      
                      'coeff_setting_vi': self.setting(cr, uid, 'VI'),
                      'qty_setting_vi_1': qty_setting_vi_1,
                      'qty_setting_vi_2': qty_setting_vi_2,
                      'qty_setting_vi_3': qty_setting_vi_3,
                      'qty_setting_vi_4': qty_setting_vi_4,
                      'qty_setting_vi_5': qty_setting_vi_5,
                      'qty_setting_vi_6': qty_setting_vi_6,
                      'qty_setting_vi_7': qty_setting_vi_7,
                      'qty_setting_vi_8': qty_setting_vi_8,
                      'qty_setting_vi_9': qty_setting_vi_9,
                      'qty_setting_vi_10': qty_setting_vi_10,
                      'qty_setting_vi_11': qty_setting_vi_11,
                      'qty_setting_vi_12': qty_setting_vi_12,
                      'qty_setting_vi_total': qty_setting_vi_1 + qty_setting_vi_2 + qty_setting_vi_3 + qty_setting_vi_4 + qty_setting_vi_5 + qty_setting_vi_6 + qty_setting_vi_7 + qty_setting_vi_8 + qty_setting_vi_9 + qty_setting_vi_10 + qty_setting_vi_11 + qty_setting_vi_12,
                      'emp_setting_vi': self.setting_employee(cr, uid, date_from, date_to, 'VI'),
                      'target_setting_vi': self.target_setting(cr, uid, 'VI'),
                      
                      'coeff_setting_vii': self.setting(cr, uid, 'VII'),
                      'qty_setting_vii_1': qty_setting_vii_1,
                      'qty_setting_vii_2': qty_setting_vii_2,
                      'qty_setting_vii_3': qty_setting_vii_3,
                      'qty_setting_vii_4': qty_setting_vii_4,
                      'qty_setting_vii_5': qty_setting_vii_5,
                      'qty_setting_vii_6': qty_setting_vii_6,
                      'qty_setting_vii_7': qty_setting_vii_7,
                      'qty_setting_vii_8': qty_setting_vii_8,
                      'qty_setting_vii_9': qty_setting_vii_9,
                      'qty_setting_vii_10': qty_setting_vii_10,
                      'qty_setting_vii_11': qty_setting_vii_11,
                      'qty_setting_vii_12': qty_setting_vii_12,
                      'qty_setting_vii_total': qty_setting_vii_1 + qty_setting_vii_2 + qty_setting_vii_3 + qty_setting_vii_4 + qty_setting_vii_5 + qty_setting_vii_6 + qty_setting_vii_7 + qty_setting_vii_8 + qty_setting_vii_9 + qty_setting_vii_10 + qty_setting_vii_11 + qty_setting_vii_12,
                      'emp_setting_vii': self.setting_employee(cr, uid, date_from, date_to, 'VII'),
                      'target_setting_vii': self.target_setting(cr, uid, 'VII'),
                      
                      'coeff_setting_viii': self.setting(cr, uid, 'VIII'),
                      'qty_setting_viii_1': qty_setting_viii_1,
                      'qty_setting_viii_2': qty_setting_viii_2,
                      'qty_setting_viii_3': qty_setting_viii_3,
                      'qty_setting_viii_4': qty_setting_viii_4,
                      'qty_setting_viii_5': qty_setting_viii_5,
                      'qty_setting_viii_6': qty_setting_viii_6,
                      'qty_setting_viii_7': qty_setting_viii_7,
                      'qty_setting_viii_8': qty_setting_viii_8,
                      'qty_setting_viii_9': qty_setting_viii_9,
                      'qty_setting_viii_10': qty_setting_viii_10,
                      'qty_setting_viii_11': qty_setting_viii_11,
                      'qty_setting_viii_12': qty_setting_viii_12,
                      'qty_setting_viii_total': qty_setting_viii_1 + qty_setting_viii_2 + qty_setting_viii_3 + qty_setting_viii_4 + qty_setting_viii_5 + qty_setting_viii_6 + qty_setting_viii_7 + qty_setting_viii_8 + qty_setting_viii_9 + qty_setting_viii_10 + qty_setting_viii_11 + qty_setting_viii_12,
                      'emp_setting_viii': self.setting_employee(cr, uid, date_from, date_to, 'VIII'),
                      'target_setting_viii': self.target_setting(cr, uid, 'VIII'),
                      
                      'coeff_setting_ix': self.setting(cr, uid, 'IX'),
                      'qty_setting_ix_1': qty_setting_ix_1,
                      'qty_setting_ix_2': qty_setting_ix_2,
                      'qty_setting_ix_3': qty_setting_ix_3,
                      'qty_setting_ix_4': qty_setting_ix_4,
                      'qty_setting_ix_5': qty_setting_ix_5,
                      'qty_setting_ix_6': qty_setting_ix_6,
                      'qty_setting_ix_7': qty_setting_ix_7,
                      'qty_setting_ix_8': qty_setting_ix_8,
                      'qty_setting_ix_9': qty_setting_ix_9,
                      'qty_setting_ix_10': qty_setting_ix_10,
                      'qty_setting_ix_11': qty_setting_ix_11,
                      'qty_setting_ix_12': qty_setting_ix_12,
                      'qty_setting_ix_total': qty_setting_ix_1 + qty_setting_ix_2 + qty_setting_ix_3 + qty_setting_ix_4 + qty_setting_ix_5 + qty_setting_ix_6 + qty_setting_ix_7 + qty_setting_ix_8 + qty_setting_ix_9 + qty_setting_ix_10 + qty_setting_ix_11 + qty_setting_ix_12,
                      'emp_setting_ix': self.setting_employee(cr, uid, date_from, date_to, 'IX'),
                      'target_setting_ix': self.target_setting(cr, uid, 'IX'),
                   }
            return {'name': name_report, 'line': arr}
    
    def _3d_level(self, cr, uid, name):
        _3d_level = self.pool.get('hpusa3d.difficulty.level')
        ids = _3d_level.search(cr, uid, [('name','=',name)])
        if ids:
            return _3d_level.browse(cr, uid, ids[0]).coefficient or 0 
        return 0
        
    def qty_3d_level(self, cr, uid, date_from, date_to, name, type, number):
        if type == 'month':
            date_start = date_from
            if number == 1:
                date_from = datetime.strptime(date_start, '%Y-%m-%d')
            else:
                days = (number - 1)*7
                date_from = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
            days = (number)*7
            date_to = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
        else:
            d = datetime.strptime(date_from, '%Y-%m-%d')
            date_from = date(d.year, 1, 1) + relativedelta(months=+(number-1))
            date_to = date(d.year, 1, 31) + relativedelta(months=+(number-1))
        _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id._3d_difficulty_level.name','=', name),('parent_id.state','=','confirmed')])
        point = len(_3d_report_ids)
        return point   
    
    def _3d_employee_level(self, cr, uid, date_from, date_to, name):
        _3d_level = self.pool.get('hpusa3d.difficulty.level')
        ids = _3d_level.search(cr, uid, [('name','=',name)]);
        if ids:
            #get report line
            _3d_report = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('product_id._3d_difficulty_level.id','=',ids[0]),('parent_id.state','=','confirmed')])
            if _3d_report:
                emp = []
                for item in _3d_report:
                    _3d = self.pool.get('hpusa.3d.report.line').browse(cr, uid, item)
                    if _3d.parent_id.designer_id:
                        if _3d.parent_id.designer_id.id not in emp:
                            emp.append(_3d.parent_id.designer_id.id)
                return len(emp);
        return 0
        
    def _3d_times(self, cr, uid, symbol, name):
        _3d_times = self.pool.get('hpusa3d.times')
        ids = _3d_times.search(cr, uid, [('name',symbol,name)]);
        if ids:
            return _3d_times.browse(cr, uid, ids[0]).coefficient or 0
        return 0
    
    def qty_3d_times(self, cr, uid, date_from, date_to, name, type, number):
        if type == 'month':
            date_start = date_from
            if number == 1:
                date_from = datetime.strptime(date_start, '%Y-%m-%d')
            else:
                days = (number - 1)*7
                date_from = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
            days = (number)*7
            date_to = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
        else:
            d = datetime.strptime(date_from, '%Y-%m-%d')
            date_from = date(d.year, 1, 1) + relativedelta(months=+(number-1))
            date_to = date(d.year, 1, 31) + relativedelta(months=+(number-1))
        if name == 4:
            _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id._3d_design_times.name','>=', name),('parent_id.state','=','confirmed')])
        else:
            _3d_report_ids = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id._3d_design_times.name','=', name),('parent_id.state','=','confirmed')])
        point = len(_3d_report_ids)
        return point
        
    def _3d_employee_times(self, cr, uid, date_from, date_to, symbol, name):
        _3d_times = self.pool.get('hpusa3d.times')
        ids = _3d_times.search(cr, uid, [('name',symbol,name)]);
        if ids:
            #get report line
            _3d_report = self.pool.get('hpusa.3d.report.line').search(cr, uid, [('product_id._3d_design_times.id','=',ids[0]),('parent_id.state','=','confirmed')])
            if _3d_report:
                emp = []
                for item in _3d_report:
                    _3d = self.pool.get('hpusa.3d.report.line').browse(cr, uid, item)
                    if _3d.parent_id.designer_id:
                        if _3d.parent_id.designer_id.id not in emp:
                            emp.append(_3d.parent_id.designer_id.id)
                return len(emp);
        return 0

    def _3d_target(self, cr, uid, name):
        _3d_target = self.pool.get('hpusa.kpis.target.3d.line')
        ids = _3d_target.search(cr, uid, [('level.name','=', name)])
        if ids:
            return _3d_target.browse(cr, uid, ids[0]).level and _3d_target.browse(cr, uid, ids[0]).level.coefficient or 0
        return 0
        
    def casting(self, cr, uid, symbol, name):
        casting = self.pool.get('hpusa.casting.times')
        ids = casting.search(cr, uid, [('name', symbol, name)])
        if ids:
            return casting.browse(cr, uid, ids[0]).coefficient_gold or 0
        return 0

    def qty_casting(self, cr, uid, date_from, date_to, name, type, number):
        if type == 'month':
            date_start = date_from
            if number == 1:
                date_from = datetime.strptime(date_start, '%Y-%m-%d')
            else:
                days = (number - 1)*7
                date_from = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
            days = (number)*7
            date_to = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
        else:
            d = datetime.strptime(date_from, '%Y-%m-%d')
            date_from = date(d.year, 1, 1) + relativedelta(months=+(number-1))
            date_to = date(d.year, 1, 31) + relativedelta(months=+(number-1))
        if name == 4:
            _casting_report_ids = self.pool.get('hpusa.casting.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id.casting_times.name','>=', name),('parent_id.state','=','confirmed')])
        else:
            _casting_report_ids = self.pool.get('hpusa.casting.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id.casting_times.name','=', name),('parent_id.state','=','confirmed')])
        point = len(_casting_report_ids)
        return point
        
    def casting_employee(self, cr, uid, date_from, date_to, symbol, name):
        casting = self.pool.get('hpusa.casting.times')
        ids = casting.search(cr, uid, [('name',symbol,name)]);
        if ids:
            #get report line
            casting_report = self.pool.get('hpusa.casting.report.line').search(cr, uid, [('product_id.casting_times.id','=',ids[0]),('parent_id.state','=','confirmed')])
            if casting_report:
                emp = []
                for item in casting_report:
                    cas = self.pool.get('hpusa.casting.report.line').browse(cr, uid, item)
                    if cas.worker:
                        if cas.worker.id not in emp:
                            emp.append(cas.worker.id)
                return len(emp);
        return 0
        
        
    def assembling(self, cr, uid, name):
        assembling = self.pool.get('hpusa.ass.difficulty.level')
        ids = assembling.search(cr, uid, [('name', '=', name)])
        if ids:
            return assembling.browse(cr, uid, ids[0]).coefficient or 0
        return 0
        
    def qty_assembling(self, cr, uid, date_from, date_to, name, type, number):
        if type == 'month':
            date_start = date_from
            if number == 1:
                date_from = datetime.strptime(date_start, '%Y-%m-%d')
            else:
                days = (number - 1)*7
                date_from = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
            days = (number)*7
            date_to = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
        else:
            d = datetime.strptime(date_from, '%Y-%m-%d')
            date_from = date(d.year, 1, 1) + relativedelta(months=+(number-1))
            date_to = date(d.year, 1, 31) + relativedelta(months=+(number-1))
        if name == 4:
            _assembling_report_ids = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id.ass_difficulty_level.name','>=', name),('parent_id.state','=','confirmed')])
        else:
            _assembling_report_ids = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id.ass_difficulty_level.name','=', name),('parent_id.state','=','confirmed')])
        point = 0
        point = len(_assembling_report_ids)
        return point
        
    def assembling_employee(self, cr, uid, date_from, date_to, name):
        assembling = self.pool.get('hpusa.ass.difficulty.level')
        ids = assembling.search(cr, uid, [('name','=',name)]);
        if ids:
            #get report line
            assembling_report = self.pool.get('hpusa.assembling.report.line').search(cr, uid, [('product_id.ass_difficulty_level.id','=',ids[0]),('parent_id.state','=','confirmed')])
            if assembling_report:
                emp = []
                for item in assembling_report:
                    ass = self.pool.get('hpusa.assembling.report.line').browse(cr, uid, item)
                    if ass.parent_id.reporter_id:
                        if ass.parent_id.reporter_id.id not in emp:
                            emp.append(ass.parent_id.reporter_id.id)
                return len(emp);
        return 0
        
    def target_assembling(self, cr, uid, name):
        target_assembling = self.pool.get('hpusa.kpis.target.assembling.line')
        ids = target_assembling.search(cr, uid, [('level.name', '=', name)])
        if ids:
            return target_assembling.browse(cr, uid, ids[0]).level and target_assembling.browse(cr, uid, ids[0]).level.coefficient or 0
        return 0
        
    def setting(self, cr, uid, name):
        setting = self.pool.get('hpusa.setting.difficulty.level')
        ids = setting.search(cr, uid, [('name', '=', name)])
        if ids:
            return setting.browse(cr, uid, ids[0]).coefficient or 0
        return 0
        
    def qty_setting(self, cr, uid, date_from, date_to, name, type, number):
        if type == 'month':
            date_start = date_from
            if number == 1:
                date_from = datetime.strptime(date_start, '%Y-%m-%d')
            else:
                days = (number - 1)*7
                date_from = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
            days = (number)*7
            date_to = datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(days=days)
        else:
            d = datetime.strptime(date_from, '%Y-%m-%d')
            date_from = date(d.year, 1, 1) + relativedelta(months=+(number-1))
            date_to = date(d.year, 1, 31) + relativedelta(months=+(number-1))
        _setting_report_ids = self.pool.get('hpusa.setting.report.line').search(cr, uid, [('parent_id.report_date','>=',date_from),('parent_id.report_date','<=',date_to),('product_id.setting_difficulty_level.name','=', name),('parent_id.state','=','confirmed')])
        point = len(_setting_report_ids)
        return point
        
    def setting_employee(self, cr, uid, date_from, date_to, name):
        setting = self.pool.get('hpusa.setting.difficulty.level')
        ids = setting.search(cr, uid, [('name','=',name)]);
        if ids:
            #get report line
            setting_report = self.pool.get('hpusa.setting.report.line').search(cr, uid, [('product_id.setting_difficulty_level.id','=',ids[0]),('parent_id.state','=','confirmed')])
            if setting_report:
                emp = []
                for item in setting_report:
                    set = self.pool.get('hpusa.setting.report.line').browse(cr, uid, item)
                    if set.parent_id.reporter_id:
                        if set.parent_id.reporter_id.id not in emp:
                            emp.append(set.parent_id.reporter_id.id)
                return len(emp);
        return 0
        
       
    def target_setting(self, cr, uid, name):
        target_setting = self.pool.get('hpusa.kpis.target.setting.line')
        ids = target_setting.search(cr, uid, [('level.name', '=', name)])
        if ids:
            return target_setting.browse(cr, uid, ids[0]).level and target_setting.browse(cr, uid, ids[0]).level.coefficient or 0
        return 0
        
wizard_hp_report_kpis()

openoffice_report.openoffice_report(
    'report.wizard_hp_report_kpis_3d',
    'wizard.hp.report.kpis.report',
    parser=wizard_hp_report_kpis
)

openoffice_report.openoffice_report(
    'report.wizard_hp_report_kpis_casting',
    'wizard.hp.report.kpis.report',
    parser=wizard_hp_report_kpis
)


openoffice_report.openoffice_report(
    'report.wizard_hp_report_kpis_assembling',
    'wizard.hp.report.kpis.report',
    parser=wizard_hp_report_kpis
)


openoffice_report.openoffice_report(
    'report.wizard_hp_report_kpis_setting',
    'wizard.hp.report.kpis.report',
    parser=wizard_hp_report_kpis
)

openoffice_report.openoffice_report(
    'report.wizard_hp_report_kpis_aggregate',
    'wizard.hp.report.kpis.report',
    parser=wizard_hp_report_kpis
)

openoffice_report.openoffice_report(
    'report.wizard_hp_report_kpis_aggregate_year',
    'wizard.hp.report.kpis.report',
    parser=wizard_hp_report_kpis
)