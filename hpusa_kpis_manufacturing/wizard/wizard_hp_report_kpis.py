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
from openerp import SUPERUSER_ID

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
        res = self.read(cr, SUPERUSER_ID, ids, ['date_from','date_to','type','option','month', 'month_from','month_to'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hp.report.kpis'
        type = res['type']
        if type == '3d':
            datas['line'] = self.print_hp_report_kpis_3d(cr, SUPERUSER_ID, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            datas['summary'] = self.summary_3d(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_3d',
                'datas'         : datas,
           }
        elif type =='casting':
            datas['line'] = self.print_hp_report_kpis_casting(cr, SUPERUSER_ID, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            datas['summary'] = self.summary_casting(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_casting',
                'datas'         : datas,
                }
        elif type =='assembling':
            datas['line'] = self.print_hp_report_kpis_assembling(cr, SUPERUSER_ID, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            datas['summary'] = self.summary_assembling(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_assembling',
                'datas'         : datas,
                }
        elif type =='setting':
            datas['line'] = self.print_hp_report_kpis_setting(cr, SUPERUSER_ID, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            datas['summary'] = self.summary_setting(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_setting',
                'datas'         : datas,
           }
        elif type =='aggregate':
            datas['line'] = self.print_hp_report_kpis_aggregate(cr, SUPERUSER_ID, res['option'], res['date_from'], res['date_to'], res['month'], res['month_from'] ,res['month_to'])
            datas['summary_3d'] = self.summary_3d(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            datas['summary_casting'] = self.summary_casting(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            datas['summary_assembling'] = self.summary_assembling(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            datas['summary_setting'] = self.summary_setting(cr, SUPERUSER_ID, datas['line']['date_from'], datas['line']['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'wizard_hp_report_kpis_aggregate',
                'datas'         : datas,
           }
            
            # else:
            #     raise osv.except_osv(('Wanning'),('General report supports only the month and year!'))
           

    def summary_3d(self, cr, uid, date_from, date_to):
        #get target in date_from date_to
        _3d_target = self.pool.get('hpusa.kpis.target.3d').search(cr, uid, [('type','=','3d'),('date_from','>=', date_from),('date_to', '<=', date_to)])
        sum_target = 0
        sum_days = 0
        sum_total = 0
        arr_target_tmp = {}
        for _3d in _3d_target:
            _3d_object = self.pool.get('hpusa.kpis.target.3d').browse(cr, uid, _3d)
            for line in _3d_object.line_ids:
                target = line.target
                days = line.number_day
                total = line.total
                if arr_target_tmp.has_key(line.employee_id.id):
                    target += arr_target_tmp[line.employee_id.id]['target']
                    days += arr_target_tmp[line.employee_id.id]['days']
                    total += arr_target_tmp[line.employee_id.id]['total']
                arr_target_tmp[line.employee_id.id] = {
                    'employee': line.employee_id.name,
                    'target': target,
                    'days': days,
                    'total': total,
                    'notes': line.notes and line.notes or '',
                }
        arr_target = []
        stt = 0
        for key in arr_target_tmp:
            stt += 0
            arr_target_tmp[key]['stt'] = stt
            arr_target.append(arr_target_tmp[key])
            sum_target += arr_target_tmp[key]['target']
            sum_days += arr_target_tmp[key]['days']
            sum_total += arr_target_tmp[key]['total']

        
        #get kpi get so luong hoan thanh va so ngay lam viec
        _3d_ids = self.pool.get('hpusa.daily.report.3d').search(cr, uid, [('type','=','3d'),('report_date','>=',date_from),('report_date','<=',date_to),('state','=','confirmed')])
        _3d_obj = self.pool.get('hpusa.daily.report.3d').browse(cr, uid, _3d_ids)
        kpi_arr_temp = {}
        total_1time = 0
        total_2times = 0
        total_3times = 0
        total_4times = 0
        total_i = 0
        total_ii = 0
        total_iii = 0
        total_iv = 0
        total_v = 0
        total_vi = 0
        total_target = 0
        total_tb_sp = 0
        total_tb = 0
        total_day_work = 0
        total_complete = 0
        total_times = 0
        total_level = 0
        total_point = 0
        for obj in _3d_obj:
            day_work = 1
            #count 
            count_1time = 0
            count_2times = 0
            count_3times = 0
            count_4times = 0
            count_i = 0
            count_ii = 0
            count_iii = 0
            count_iv = 0
            count_v = 0
            count_vi = 0
            point = 0
            complete = 0
            #count 
            for line in obj.line_ids:
                #sum_count
                # lan kpi trung voi lan trong product
                if line.product_id._3d_design_times and line._3d_design_times.id == line.product_id._3d_design_times.id:
                    if line.product_id._3d_design_times:
                        if line.product_id._3d_design_times.name == 1:
                            count_1time += line.complete
                        elif line.product_id._3d_design_times.name == 2:
                            count_2times += line.complete
                        elif line.product_id._3d_design_times.name == 3:
                            count_3times += line.complete
                        elif  line.product_id._3d_design_times.name > 3:
                            count_4times += line.complete

                    if line.product_id._3d_difficulty_level:
                        if line.product_id._3d_difficulty_level.name == 'I':
                            count_i += line.complete
                        elif line.product_id._3d_difficulty_level.name == 'II':
                            count_ii += line.complete
                        elif line.product_id._3d_difficulty_level.name == 'III':
                            count_iii += line.complete
                        elif line.product_id._3d_difficulty_level.name == 'IV':
                            count_iv += line.complete
                        elif line.product_id._3d_difficulty_level.name == 'V':
                            count_v += line.complete
                        elif line.product_id._3d_difficulty_level.name == 'VI':
                            count_vi += line.complete               
                    #sum_count
                    complete += line.complete
                    point += line.point

            if kpi_arr_temp.has_key(obj.designer_id.id):
                complete += kpi_arr_temp[obj.designer_id.id]['complete']
                day_work += kpi_arr_temp[obj.designer_id.id]['day_work']
                count_1time += kpi_arr_temp[obj.designer_id.id]['count_1time']
                count_2times += kpi_arr_temp[obj.designer_id.id]['count_2times']
                count_3times += kpi_arr_temp[obj.designer_id.id]['count_3times']
                count_4times += kpi_arr_temp[obj.designer_id.id]['count_4times']
                count_i += kpi_arr_temp[obj.designer_id.id]['count_i']
                count_ii += kpi_arr_temp[obj.designer_id.id]['count_ii']
                count_iii += kpi_arr_temp[obj.designer_id.id]['count_iii']
                count_iv += kpi_arr_temp[obj.designer_id.id]['count_iv']
                count_v += kpi_arr_temp[obj.designer_id.id]['count_v']
                count_vi += kpi_arr_temp[obj.designer_id.id]['count_vi']
                point += kpi_arr_temp[obj.designer_id.id]['point']
            
            kpi_arr_temp[obj.designer_id.id] = {
                                                    'name': obj.designer_id.name, 'point': point, 'complete': complete, 'day_work': day_work,
                                                    'count_1time': count_1time, 'count_2times': count_2times, 'count_3times': count_3times,
                                                    'count_4times': count_4times, 'count_i': count_i, 'count_ii': count_ii,
                                                    'count_iii': count_iii, 'count_iv': count_iv, 'count_v': count_v,
                                                    'count_vi': count_vi, 'tb_sp': day_work and round(complete / day_work, 2)  or 0, 'tb': day_work and round(point / day_work, 2)  or 0
                                                }

        arr_kpi = []
        stt = 0
        for key in kpi_arr_temp:
            stt = stt + 1
            #get target
            emp_target = 0
            if arr_target_tmp.has_key(key):
                emp_target = arr_target_tmp[key]['total']

            kpi_arr_temp[key]['target'] = emp_target
            kpi_arr_temp[key]['percent'] = emp_target and round(kpi_arr_temp[key]['point'] * 100/ emp_target, 2) or 0 
            kpi_arr_temp[key]['total_time'] = kpi_arr_temp[key]['count_1time'] + kpi_arr_temp[key]['count_2times'] + kpi_arr_temp[key]['count_3times'] + kpi_arr_temp[key]['count_4times']
            kpi_arr_temp[key]['percent_1'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_1time'] * 100 / kpi_arr_temp[key]['total_time'] , 2) or 0
            kpi_arr_temp[key]['percent_2'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_2times'] * 100 / kpi_arr_temp[key]['total_time'], 2) or 0
            kpi_arr_temp[key]['percent_3'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_3times'] * 100 / kpi_arr_temp[key]['total_time'], 2) or 0
            kpi_arr_temp[key]['percent_4'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_4times'] * 100 / kpi_arr_temp[key]['total_time'], 2) or 0

            kpi_arr_temp[key]['total_level'] = kpi_arr_temp[key]['count_i'] + kpi_arr_temp[key]['count_ii'] + kpi_arr_temp[key]['count_iii'] + kpi_arr_temp[key]['count_iv'] + kpi_arr_temp[key]['count_v'] + kpi_arr_temp[key]['count_vi']
            kpi_arr_temp[key]['percent_i'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_i'] * 100 / kpi_arr_temp[key]['total_level'] , 2) or 0
            kpi_arr_temp[key]['percent_ii'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_ii'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_iii'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_iii'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_iv'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_iv'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_v'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_v'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_vi'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_vi'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            

            kpi_arr_temp[key]['stt'] = stt
            arr_kpi.append(kpi_arr_temp[key])

            total_target += emp_target
            total_times += kpi_arr_temp[key]['total_time']
            total_level += kpi_arr_temp[key]['total_level']

            total_1time += kpi_arr_temp[key]['count_1time']
            total_2times += kpi_arr_temp[key]['count_2times']
            total_3times +=  kpi_arr_temp[key]['count_3times']
            total_4times += kpi_arr_temp[key]['count_4times']
            total_i += kpi_arr_temp[key]['count_i']
            total_ii += kpi_arr_temp[key]['count_ii']
            total_iii +=  kpi_arr_temp[key]['count_iii']
            total_iv += kpi_arr_temp[key]['count_iv']
            total_v += kpi_arr_temp[key]['count_v']
            total_vi += kpi_arr_temp[key]['count_vi']
            total_tb_sp +=  kpi_arr_temp[key]['tb_sp'] 
            total_tb +=  kpi_arr_temp[key]['tb'] 
            total_day_work += kpi_arr_temp[key]['day_work']
            total_complete += kpi_arr_temp[key]['complete']
            total_point += kpi_arr_temp[key]['point']


        total_percent_target = round(total_target and total_point * 100 / total_target , 2) or 0
        total_percent_1 = round( total_times and total_1time * 100 / total_times, 2) or 0
        total_percent_2 = round( total_times and total_2times * 100 / total_times, 2) or 0
        total_percent_3 = round( total_times and total_3times * 100 / total_times, 2) or 0
        total_percent_4 = round( total_times and total_4times * 100 / total_times, 2) or 0
        total_percent_i = round( total_level and total_i * 100 / total_level, 2) or 0
        total_percent_ii = round( total_level and total_ii * 100 / total_level, 2) or 0
        total_percent_iii = round( total_level and total_iii * 100 / total_level, 2) or 0
        total_percent_iv = round( total_level and total_iv * 100 / total_level, 2) or 0
        total_percent_v = round( total_level and total_v * 100 / total_level, 2) or 0
        total_percent_vi = round( total_level and total_vi * 100 / total_level, 2) or 0

        result = {}
        result['target'] = {'res': arr_target, 'sum_target': sum_target, 'sum_days': sum_days, 'sum_total': sum_total}
        result['kpi'] = {'res': arr_kpi, 'total_1time': total_1time, 'total_2times': total_2times, 'total_3times': total_3times, 'total_4times': total_4times, 'total_i': total_i, 'total_ii': total_ii, 'total_iii': total_iii, 'total_iv': total_iv, 'total_v': total_v, 'total_vi': total_vi, 'total_tb': total_tb, 'total_day_work': total_day_work, 'total_complete': total_complete,
                        'total_target': total_target, 'total_percent_1': total_percent_1, 'total_percent_2': total_percent_2, 'total_percent_3': total_percent_3, 'total_percent_4': total_percent_4, 'total_percent_i': total_percent_i, 'total_percent_ii': total_percent_ii, 'total_percent_iii': total_percent_iii, 'total_percent_iv': total_percent_iv, 'total_percent_v': total_percent_v, 'total_percent_vi': total_percent_vi,
                        'total_times': total_times, 'total_level': total_level, 'total_percent_target': total_percent_target, 'total_point': total_point, 'total_tb_sp': total_tb_sp}

        return result


    def print_hp_report_kpis_3d(self, cr, uid, type, date_from, date_to, month, month_from, month_to):
        #report week
        name_report = ''
        if type == 'month':
            period = self.pool.get('account.period').browse(cr, uid, month[0])
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
            s_total_co_level = 0
            for line_3d in groups[key]:
                if line_3d.product_id._3d_design_times and line_3d._3d_design_times.id == line_3d.product_id._3d_design_times.id:
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
                    
                    
                            
                    coefficient_lv = line_3d.product_id._3d_difficulty_level and line_3d.product_id._3d_difficulty_level.coefficient or 0
                    total_coeff_lv = (i + ii + iii + iv + v + vi) * coefficient_lv # (6)=(4)*(5)
                    #times
                    _3d_times = line_3d.product_id._3d_design_times and line_3d.product_id._3d_design_times.name or 0
                    coefficient_3d_times = line_3d.product_id._3d_design_times and line_3d.product_id._3d_design_times.coefficient or 0
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
                    s_total_co_level += total_coeff_lv
                    s_total_co += total_coeff_lv * _3d_times * coefficient_3d_times
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
                                })
            re = {'line': arr, 's_i': s_i, 's_ii': s_ii, 's_iii': s_iii, 's_iv': s_iv, 's_v': s_v, 's_vi': s_vi, 's_level': s_level, 's_coeff': s_coeff, 's_times': s_times, 's_co_times': s_co_times, 's_total_co': s_total_co, 's_total_co_level': s_total_co_level}
            result.append(re)
        return {'name': name_report, 'result': result, 'date_from': date_from, 'date_to': date_to}
    

    def summary_casting(self, cr, uid, date_from, date_to):
        #get target in date_from date_to
        _casting_target = self.pool.get('hpusa.kpis.target.casting').search(cr, uid, [('date_from','>=', date_from),('date_to', '<=', date_to)])
        arr_target = []
        sum_target = 0
        sum_days = 0
        sum_total = 0
        arr_target_tmp = {}
        for _casting in _casting_target:
            _casting_object = self.pool.get('hpusa.kpis.target.casting').browse(cr, uid, _casting)
            for line in _casting_object.line_ids:
                target = line.target
                days = line.day_month
                total = line.total
                if arr_target_tmp.has_key(line.employee_id.id):
                    target += arr_target_tmp[line.employee_id.id]['target']
                    days += arr_target_tmp[line.employee_id.id]['days']
                    total += arr_target_tmp[line.employee_id.id]['total']
                arr_target_tmp[line.employee_id.id] = {
                    'employee': line.employee_id.name,
                    'target': target,
                    'days': days,
                    'total': total,
                    'notes': line.notes and line.notes or '',
                }
        arr_target = []
        stt = 0
        for key in arr_target_tmp:
            stt += 0
            arr_target_tmp[key]['stt'] = stt
            arr_target.append(arr_target_tmp[key])
            sum_target += arr_target_tmp[key]['target']
            sum_days += arr_target_tmp[key]['days']
            sum_total += arr_target_tmp[key]['total']
        
        #get kpi get so luong hoan thanh va so ngay lam viec
        _casting_ids = self.pool.get('hpusa.daily.report.casting').search(cr, uid, [('report_date','>=',date_from),('report_date','<=',date_to),('state','=','confirmed')])
        _casting_obj = self.pool.get('hpusa.daily.report.casting').browse(cr, uid, _casting_ids)
        kpi_arr_temp = {}
        total_1time = 0
        total_2times = 0
        total_3times = 0
        total_4times = 0
        total_target = 0
        total_tb = 0
        total_tb_sp = 0
        total_day_work = 0
        total_complete = 0
        total_times = 0
        total_point = 0
        for obj in _casting_obj:
            
            #duyet 1 phieu la 1 ngay
            arr = []
            for line in obj.line_ids:
                if line.product_id.casting_times and line.casting_times.id == line.product_id.casting_times.id:
                #count 
                    count_1time = 0
                    count_2times = 0
                    count_3times = 0
                    count_4times = 0
                    #count 

                    #xet employee da co trong pheu roi khong tinh ngay nua
                    day_work = 0
                    if line.worker.id not in arr:
                        day_work = 1
                    arr.append(line.worker.id)

                    #sum_count
                    if line.product_id.casting_times:
                        if line.product_id.casting_times.name == 1:
                            count_1time += line.complete
                        elif line.product_id.casting_times.name == 2:
                            count_2times += line.complete
                        elif line.product_id.casting_times.name == 3:
                            count_3times += line.complete
                        elif  line.product_id.casting_times.name > 3:
                            count_4times += line.complete

                    #sum_count
                    complete = line.complete
                    point = line.point

                    if kpi_arr_temp.has_key(line.worker.id):
                        complete += kpi_arr_temp[line.worker.id]['complete']
                        day_work += kpi_arr_temp[line.worker.id]['day_work']
                        count_1time += kpi_arr_temp[line.worker.id]['count_1time']
                        count_2times += kpi_arr_temp[line.worker.id]['count_2times']
                        count_3times += kpi_arr_temp[line.worker.id]['count_3times']
                        count_4times += kpi_arr_temp[line.worker.id]['count_4times']
                        point += kpi_arr_temp[line.worker.id]['point']

                    kpi_arr_temp[line.worker.id] = {
                                                        'name': line.worker.name, 'complete': complete, 'day_work': day_work, 'point': point,
                                                        'count_1time': count_1time, 'count_2times': count_2times, 'count_3times': count_3times,
                                                        'count_4times': count_4times, 'tb_sp': day_work and round(complete / day_work, 2)  or 0,
                                                        'tb': day_work and round(point / day_work, 2)  or 0
                                                    }

        arr_kpi = []
        stt = 0
        for key in kpi_arr_temp:
            stt = stt + 1
            #get target
            emp_target = 0
            if arr_target_tmp.has_key(key):
                emp_target = arr_target_tmp[key]['total']

            kpi_arr_temp[key]['target'] = emp_target
            kpi_arr_temp[key]['percent'] = emp_target and round(kpi_arr_temp[key]['point'] * 100 / emp_target, 2) or 0
            kpi_arr_temp[key]['total_time'] = kpi_arr_temp[key]['count_1time'] + kpi_arr_temp[key]['count_2times'] + kpi_arr_temp[key]['count_3times'] + kpi_arr_temp[key]['count_4times']
            kpi_arr_temp[key]['percent_1'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_1time'] * 100 / kpi_arr_temp[key]['total_time'] , 2) or 0
            kpi_arr_temp[key]['percent_2'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_2times'] * 100 / kpi_arr_temp[key]['total_time'], 2) or 0
            kpi_arr_temp[key]['percent_3'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_3times'] * 100 / kpi_arr_temp[key]['total_time'], 2) or 0
            kpi_arr_temp[key]['percent_4'] = kpi_arr_temp[key]['total_time'] > 0 and round(kpi_arr_temp[key]['count_4times'] * 100 / kpi_arr_temp[key]['total_time'], 2) or 0

            kpi_arr_temp[key]['stt'] = stt
            arr_kpi.append(kpi_arr_temp[key])
            total_target += emp_target
            total_times += kpi_arr_temp[key]['total_time']


            total_1time += kpi_arr_temp[key]['count_1time']
            total_2times += kpi_arr_temp[key]['count_2times']
            total_3times += kpi_arr_temp[key]['count_3times']
            total_4times += kpi_arr_temp[key]['count_4times']
            total_tb += kpi_arr_temp[key]['tb']
            total_tb_sp += kpi_arr_temp[key]['tb_sp']
            total_day_work +=  kpi_arr_temp[key]['day_work']
            total_complete += kpi_arr_temp[key]['complete']
            total_point += kpi_arr_temp[key]['point']


        total_percent_target = round(total_target and total_point * 100 / total_target , 2) or 0
        total_percent_1 = round( total_times and total_1time * 100 / total_times, 2) or 0
        total_percent_2 = round( total_times and total_2times * 100 / total_times, 2) or 0
        total_percent_3 = round( total_times and total_3times * 100 / total_times, 2) or 0
        total_percent_4 = round( total_times and total_4times * 100 / total_times, 2) or 0

        result = {}
        result['target'] = {'res': arr_target, 'sum_target': sum_target, 'sum_days': sum_days, 'sum_total': sum_total}
        
        result['kpi'] = {'res': arr_kpi, 'total_1time': total_1time, 'total_2times': total_2times, 'total_3times': total_3times, 'total_4times': total_4times, 'total_tb':  total_tb, 'total_day_work': total_day_work, 'total_complete': total_complete,
                        'total_target': total_target, 'total_percent_1': total_percent_1, 'total_percent_2': total_percent_2, 'total_percent_3': total_percent_3, 'total_percent_4': total_percent_4,
                        'total_times': total_times, 'total_percent_target': total_percent_target, 'total_point': total_point, 'total_tb_sp': total_tb_sp}

        return result

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
                if line_casting.product_id.casting_times and line_casting.casting_times.id == line_casting.product_id.casting_times.id:
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
    #                   
                    s_1 += _1_time
                    s_2 += _2_times
                    s_3 += _3_times
                    s_4 += _4_times
                    s_coff += coefficient
                    s_total_coeff += total_coeff
                    
                    
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
                                }) 
        return {'date_from': date_from, 'date_to': date_to, 'name': name_report, 'line': arr, 's_1': s_1, 's_2': s_2, 's_3': s_3, 's_4': s_4, 's_coff': s_coff, 's_total_coeff': s_total_coeff}
    
    
    def summary_assembling(self, cr, uid, date_from, date_to):
        #get target in date_from date_to
        _assembling_target = self.pool.get('hpusa.kpis.target.assembling').search(cr, uid, [('type','=','assembling'),('date_from','>=', date_from),('date_to', '<=', date_to)])
        arr_target = []
        sum_target = 0
        sum_days = 0
        sum_total = 0

        arr_target_tmp = {}
        for _assembling in _assembling_target:
            _assembling_object = self.pool.get('hpusa.kpis.target.assembling').browse(cr, uid, _assembling)
            for line in _assembling_object.line_ids:
                target = line.target
                days = line.day_month
                total = line.total
                if arr_target_tmp.has_key(line.employee_id.id):
                    target += arr_target_tmp[line.employee_id.id]['target']
                    days += arr_target_tmp[line.employee_id.id]['days']
                    total += arr_target_tmp[line.employee_id.id]['total']
                arr_target_tmp[line.employee_id.id] = {
                    'employee': line.employee_id.name,
                    'target': target,
                    'days': days,
                    'total': total,
                    'notes': line.notes and line.notes or '',
                }
        arr_target = []
        stt = 0
        for key in arr_target_tmp:
            stt += 0
            arr_target_tmp[key]['stt'] = stt
            arr_target.append(arr_target_tmp[key])
            sum_target += arr_target_tmp[key]['target']
            sum_days += arr_target_tmp[key]['days']
            sum_total += arr_target_tmp[key]['total']

        
        #get kpi get so luong hoan thanh va so ngay lam viec
        _assembling_ids = self.pool.get('hpusa.daily.report.assembling').search(cr, uid, [('type','=','assembling'),('report_date','>=',date_from),('report_date','<=',date_to),('state','=','confirmed')])
        _assembling_obj = self.pool.get('hpusa.daily.report.assembling').browse(cr, uid, _assembling_ids)
        kpi_arr_temp = {}
        total_i = 0
        total_ii = 0
        total_iii = 0
        total_iv = 0
        total_v = 0
        total_vi = 0
        total_target = 0
        total_tb = 0
        total_tb_sp = 0
        total_day_work = 0
        total_complete = 0
        total_level = 0
        total_point = 0
        for obj in _assembling_obj:
            arr = []
            for line in obj.line_ids:
                #count 
                count_i = 0
                count_ii = 0
                count_iii = 0
                count_iv = 0
                count_v = 0
                count_vi = 0
                #count 
                #sum_count
                day_work = 0
                if line.worker.id not in arr:
                    day_work = 1
                arr.append(line.worker.id)

                if line.product_id.ass_difficulty_level:
                    if line.product_id.ass_difficulty_level.name == 'I':
                        count_i += line.complete
                    elif line.product_id.ass_difficulty_level.name == 'II':
                        count_ii += line.complete
                    elif line.product_id.ass_difficulty_level.name == 'III':
                        count_iii += line.complete
                    elif line.product_id.ass_difficulty_level.name == 'IV':
                        count_iv += line.complete
                    elif line.product_id.ass_difficulty_level.name == 'V':
                        count_v += line.complete
                    elif line.product_id.ass_difficulty_level.name == 'VI':
                        count_vi += line.complete              
                #sum_count
                complete = line.complete
                point = line.point

                if kpi_arr_temp.has_key(line.worker.id):
                    complete += kpi_arr_temp[line.worker.id]['complete']
                    day_work += kpi_arr_temp[line.worker.id]['day_work']
                    count_i += kpi_arr_temp[line.worker.id]['count_i']
                    count_ii += kpi_arr_temp[line.worker.id]['count_ii']
                    count_iii += kpi_arr_temp[line.worker.id]['count_iii']
                    count_iv += kpi_arr_temp[line.worker.id]['count_iv']
                    count_v += kpi_arr_temp[line.worker.id]['count_v']
                    count_vi += kpi_arr_temp[line.worker.id]['count_vi']
                    point += kpi_arr_temp[line.worker.id]['point']

                kpi_arr_temp[line.worker.id] = {
                                                    'name': line.worker.name, 'complete': complete, 'day_work': day_work, 'point': point,
                                                    'count_i': count_i, 'count_ii': count_ii,
                                                    'count_iii': count_iii, 'count_iv': count_iv, 'count_v': count_v,
                                                    'count_vi': count_vi, 'tb_sp': day_work and round(complete / day_work, 2)  or 0, 'tb': day_work and round(point / day_work, 2)  or 0
                                                }
            
        arr_kpi = []
        stt = 0
        for key in kpi_arr_temp:
            stt = stt + 1
            #get target
            _assembling_target = self.pool.get('hpusa.kpis.target.assembling.line').search(cr, uid, [('parent_id.type','=','assembling'),('parent_id.date_from','>=', date_from),('parent_id.date_to', '<=', date_to), ('employee_id', '=', key)])
            emp_target = 0
            if arr_target_tmp.has_key(key):
                emp_target = arr_target_tmp[key]['total']
            kpi_arr_temp[key]['target'] = emp_target
            kpi_arr_temp[key]['percent'] = emp_target and round(kpi_arr_temp[key]['point'] * 100/ emp_target, 2) or 0

            kpi_arr_temp[key]['total_level'] = kpi_arr_temp[key]['count_i'] + kpi_arr_temp[key]['count_ii'] + kpi_arr_temp[key]['count_iii'] + kpi_arr_temp[key]['count_iv'] + kpi_arr_temp[key]['count_v'] + kpi_arr_temp[key]['count_vi']
            kpi_arr_temp[key]['percent_i'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_i'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_ii'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_ii'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_iii'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_iii'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_iv'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_iv'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_v'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_v'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_vi'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_vi'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['stt'] = stt
            arr_kpi.append(kpi_arr_temp[key])

            total_target += emp_target
            total_level += kpi_arr_temp[key]['total_level']


            total_i += kpi_arr_temp[key]['count_i']
            total_ii += kpi_arr_temp[key]['count_ii']
            total_iii +=  kpi_arr_temp[key]['count_iii']
            total_iv += kpi_arr_temp[key]['count_iv']
            total_v += kpi_arr_temp[key]['count_v']
            total_vi += kpi_arr_temp[key]['count_vi']
            total_tb +=  kpi_arr_temp[key]['tb']
            total_tb_sp += kpi_arr_temp[key]['tb_sp']
            total_day_work += kpi_arr_temp[key]['day_work']
            total_complete += kpi_arr_temp[key]['complete']
            total_point += kpi_arr_temp[key]['point']
        

        total_percent_target = round(total_target and total_point * 100 / total_target , 2) or 0
        total_percent_i = round( total_level and total_i * 100 / total_level, 2) or 0
        total_percent_ii = round( total_level and total_ii * 100 / total_level, 2) or 0
        total_percent_iii = round( total_level and total_iii * 100 / total_level, 2) or 0
        total_percent_iv = round( total_level and total_iv * 100 / total_level, 2) or 0
        total_percent_v = round( total_level and total_v * 100 / total_level, 2) or 0
        total_percent_vi = round( total_level and total_vi * 100 / total_level, 2) or 0

        result = {}
        result['target'] = {'res': arr_target, 'sum_target': sum_target, 'sum_days': sum_days, 'sum_total': sum_total}
        result['kpi'] = {'res': arr_kpi, 'total_i': total_i, 'total_ii': total_ii, 'total_iii': total_iii, 'total_iv': total_iv, 'total_v': total_v, 'total_vi': total_vi, 'total_tb': total_tb, 'total_day_work': total_day_work, 'total_complete': total_complete,
                        'total_target': total_target, 'total_percent_i': total_percent_i, 'total_percent_ii': total_percent_ii, 'total_percent_iii': total_percent_iii, 'total_percent_iv': total_percent_iv, 'total_percent_v': total_percent_v, 'total_percent_vi': total_percent_vi,
                        'total_level': total_level, 'total_percent_target': total_percent_target, 'total_point': total_point, 'total_tb_sp': total_tb_sp}

        return result

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
                            })
        return {'date_from': date_from, 'date_to': date_to, 'name': name_report, 'line': arr, 's_i': s_i, 's_ii': s_ii, 's_iii': s_iii, 's_iv': s_iv, 's_v': s_v, 's_vi': s_vi,
                's_percent': s_percent, 's_coeff': s_coeff, 's_total_coeff': s_total_coeff}
    
    
    def summary_setting(self, cr, uid, date_from, date_to):
        #get target in date_from date_to
        _setting_target = self.pool.get('hpusa.kpis.target.setting').search(cr, uid, [('type','=','setting'),('date_from','>=', date_from),('date_to', '<=', date_to)])
        arr_target = []
        sum_target = 0
        sum_days = 0
        sum_total = 0

        arr_target_tmp = {}
        for _setting in _setting_target:
            _setting_object = self.pool.get('hpusa.kpis.target.setting').browse(cr, uid, _setting)
            for line in _setting_object.line_ids:
                target = line.target
                days = line.day_month
                total = line.total
                if arr_target_tmp.has_key(line.employee_id.id):
                    target += arr_target_tmp[line.employee_id.id]['target']
                    days += arr_target_tmp[line.employee_id.id]['days']
                    total += arr_target_tmp[line.employee_id.id]['total']
                arr_target_tmp[line.employee_id.id] = {
                    'employee': line.employee_id.name,
                    'target': target,
                    'days': days,
                    'total': total,
                    'notes': line.notes and line.notes or '',
                }
        arr_target = []
        stt = 0
        for key in arr_target_tmp:
            stt += 0
            arr_target_tmp[key]['stt'] = stt
            arr_target.append(arr_target_tmp[key])
            sum_target += arr_target_tmp[key]['target']
            sum_days += arr_target_tmp[key]['days']
            sum_total += arr_target_tmp[key]['total']

        
        #get kpi get so luong hoan thanh va so ngay lam viec
        _setting_ids = self.pool.get('hpusa.daily.report.setting').search(cr, uid, [('type','=','setting'),('report_date','>=',date_from),('report_date','<=',date_to),('state','=','confirmed')])
        _assembling_obj = self.pool.get('hpusa.daily.report.setting').browse(cr, uid, _setting_ids)
        kpi_arr_temp = {}
        total_i = 0
        total_ii = 0
        total_iii = 0
        total_iv = 0
        total_v = 0
        total_vi = 0
        total_target = 0
        total_tb = 0
        total_tb_sp = 0
        total_day_work = 0
        total_complete = 0
        total_level = 0
        total_point = 0
        for obj in _assembling_obj:
            arr = []
            for line in obj.line_ids:
                day_work = 0
                if line.worker.id not in arr:
                    day_work = 1
                arr.append(line.worker.id)
                #count 
                count_i = 0
                count_ii = 0
                count_iii = 0
                count_iv = 0
                count_v = 0
                count_vi = 0
                #count 
                #sum_count

                if line.product_id.setting_difficulty_level:
                    if line.product_id.setting_difficulty_level.name == 'I':
                        count_i += line.complete
                    elif line.product_id.setting_difficulty_level.name == 'II':
                        count_ii += line.complete
                    elif line.product_id.setting_difficulty_level.name == 'III':
                        count_iii += line.complete
                    elif line.product_id.setting_difficulty_level.name == 'IV':
                        count_iv += line.complete
                    elif line.product_id.setting_difficulty_level.name == 'V':
                        count_v += line.complete
                    elif line.product_id.setting_difficulty_level.name == 'VI':
                        count_vi += line.complete               
                #sum_count
                complete = line.complete
                point = line.point
                if kpi_arr_temp.has_key(line.worker.id):
                    complete += kpi_arr_temp[line.worker.id]['complete']
                    day_work += kpi_arr_temp[line.worker.id]['day_work']
                    count_i += kpi_arr_temp[line.worker.id]['count_i']
                    count_ii += kpi_arr_temp[line.worker.id]['count_ii']
                    count_iii += kpi_arr_temp[line.worker.id]['count_iii']
                    count_iv += kpi_arr_temp[line.worker.id]['count_iv']
                    count_v += kpi_arr_temp[line.worker.id]['count_v']
                    count_vi += kpi_arr_temp[line.worker.id]['count_vi']
                    point += kpi_arr_temp[line.worker.id]['point']

                kpi_arr_temp[line.worker.id] = {
                                                        'name': line.worker.name, 'complete': complete, 'day_work': day_work, 'point': point,
                                                        'count_i': count_i, 'count_ii': count_ii,
                                                        'count_iii': count_iii, 'count_iv': count_iv, 'count_v': count_v,
                                                        'count_vi': count_vi, 'tb_sp': day_work and round(complete / day_work, 2)  or 0, 'tb': day_work and round(point / day_work, 2)  or 0
                                                }
        
        arr_kpi = []
        stt = 0
        for key in kpi_arr_temp:
            stt = stt + 1
            #get target
            emp_target = 0
            if arr_target_tmp.has_key(key):
                emp_target = arr_target_tmp[key]['total']

            kpi_arr_temp[key]['target'] = emp_target
            kpi_arr_temp[key]['percent'] = emp_target and round(kpi_arr_temp[key]['point'] * 100 / emp_target, 2) or 0

            kpi_arr_temp[key]['total_level'] = kpi_arr_temp[key]['count_i'] + kpi_arr_temp[key]['count_ii'] + kpi_arr_temp[key]['count_iii'] + kpi_arr_temp[key]['count_iv'] + kpi_arr_temp[key]['count_v'] + kpi_arr_temp[key]['count_vi']
            kpi_arr_temp[key]['percent_i'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_i'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_ii'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_ii'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_iii'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_iii'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_iv'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_iv'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_v'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_v'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['percent_vi'] = kpi_arr_temp[key]['total_level'] > 0 and round(kpi_arr_temp[key]['count_vi'] * 100 / kpi_arr_temp[key]['total_level'], 2) or 0
            kpi_arr_temp[key]['stt'] = stt
            arr_kpi.append(kpi_arr_temp[key])

            total_target += emp_target
            total_level += kpi_arr_temp[key]['total_level']

            total_i += kpi_arr_temp[key]['count_i']
            total_ii += kpi_arr_temp[key]['count_ii']
            total_iii +=  kpi_arr_temp[key]['count_iii']
            total_iv += kpi_arr_temp[key]['count_iv']
            total_v += kpi_arr_temp[key]['count_v']
            total_vi += kpi_arr_temp[key]['count_vi']
            total_tb +=  kpi_arr_temp[key]['tb']
            total_tb_sp +=  kpi_arr_temp[key]['tb_sp']
            total_day_work += kpi_arr_temp[key]['day_work']
            total_complete += kpi_arr_temp[key]['complete']
            total_point += kpi_arr_temp[key]['point']
            

        total_percent_target = round(total_target and total_point * 100 / total_target , 2) or 0
        total_percent_i = round( total_level and total_i * 100 / total_level, 2) or 0
        total_percent_ii = round( total_level and total_ii * 100 / total_level, 2) or 0
        total_percent_iii = round( total_level and total_iii * 100 / total_level, 2) or 0
        total_percent_iv = round( total_level and total_iv * 100 / total_level, 2) or 0
        total_percent_v = round( total_level and total_v * 100 / total_level, 2) or 0
        total_percent_vi = round( total_level and total_vi * 100 / total_level, 2) or 0

        result = {}
        result['target'] = {'res': arr_target, 'sum_target': sum_target, 'sum_days': sum_days, 'sum_total': sum_total}
        result['kpi'] = {'res': arr_kpi, 'total_i': total_i, 'total_ii': total_ii, 'total_iii': total_iii, 'total_iv': total_iv, 'total_v': total_v, 'total_vi': total_vi, 'total_tb': total_tb, 'total_day_work': total_day_work, 'total_complete': total_complete,
                        'total_target': total_target, 'total_percent_i': total_percent_i, 'total_percent_ii': total_percent_ii, 'total_percent_iii': total_percent_iii, 'total_percent_iv': total_percent_iv, 'total_percent_v': total_percent_v, 'total_percent_vi': total_percent_vi,
                        'total_level': total_level, 'total_percent_target': total_percent_target, 'total_point': total_point, 'total_tb_sp': total_tb_sp}

        return result

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
                            })
        return {'date_from': date_from, 'date_to': date_to, 'name': name_report, 'line': arr, 's_i': s_i, 's_ii': s_ii, 's_iii': s_iii, 's_iv': s_iv, 's_v': s_v,
                's_vi': s_vi, 's_vii': s_vii, 's_viii': s_viii, 's_ix': s_ix, 's_per': s_per, 's_coeff': s_coeff, 's_total_coeff': s_total_coeff
                }

        
    def print_hp_report_kpis_aggregate(self, cr, uid, type, date_from, date_to, month, month_from, month_to):
        #report week
        arr = []
        name_report = ''
        if type == 'month':
            period = self.pool.get('account.period').browse(cr, uid, month[0])
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
            
            
        return {'date_from': date_from, 'date_to': date_to, 'name': name_report}
    
    
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