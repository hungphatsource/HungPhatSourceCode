import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import time

class hpusa_daily_report(osv.osv):
    _name = 'hpusa.daily.report'
    _inherit = ['mail.thread']
    _description = "Hpusa Daily Report"
    
    def _getemployee(self, cr, uid, context=None):

        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], order = 'id DESC', limit = 1)
        if employee_ids:
            return employee_ids[0]; 
        return;  
    
    def _get_total_point(self, cr, uid, ids ,field_name, arg, context = None):
        return 0
    
    _columns = {
        'name': fields.char('Name',required=True),
        'report_date': fields.date('Date Report', required=True),
        'hp_create_date': fields.date('Create Date', required=True),
        'reporter_id': fields.many2one('hr.employee', 'Reporter',required=True),
        'user_id': fields.many2one('res.users','User',required=True), 
        'week': fields.many2one('hpusa.manufacturing.planning','Week'),
        'total_point': fields.function(_get_total_point,type='float',string='Total point', track_visibility='onchange'),
        'invoice_manager': fields.many2one('res.users', 'Invoice manager',required=True),
        'group_id': fields.many2one('hpusa.groups', 'Groups', required=True),
        'company_id': fields.many2one('res.company','Company',required=True),
        'type': fields.selection([
                            ('3d', '3D Design'),
                            ('casting', 'Casting'),
                            ('assembling', 'Assembling'),
                            ('setting', 'Setting'),
                            ], 'Type',select=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange',
        ),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        'user_id': lambda s, c, uid, ctx: uid,
        'state': 'draft',
        'report_date': lambda *a: time.strftime('%Y-%m-%d'),
        'hp_create_date': lambda *a: time.strftime('%Y-%m-%d'),
        'reporter_id': _getemployee,
    }   
    
    def action_confirm(self, cr, uid, ids, context=None):
        if not ids:
            return
        self.write(cr, uid, ids, {'state':'confirmed'}, context)
        
    def action_cancel(self, cr, uid, ids, context=None):
        if not ids:
            return
        self.write(cr, uid, ids, {'state':'cancel'}, context)
        
    def action_set_to_draft(self, cr, uid, ids, context=None):
        if not ids:
            return
        self.write(cr, uid, ids, {'state':'draft'}, context)
                
         
hpusa_daily_report()
    
class hpusa_daily_report_3d(osv.osv):
    _name = "hpusa.daily.report.3d"
    _table = "hpusa_daily_report"
    _inherit = "hpusa.daily.report" 
    def _get_total_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            sum = 0.0
            for line in  obj.line_ids:
                sum += line.point
            res[obj.id] = sum
        return res
    
    _columns = {
        'total_point': fields.function(_get_total_point,type='float',string='Total point', track_visibility='onchange'),
        'designer_id': fields.many2one('hr.employee', 'Designer',required=True),
        'line_ids': fields.one2many('hpusa.3d.report.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': '3d',
    }  

    def action_update(self, cr, uid, ids, context):
        obj_ids = self.search(cr, uid, [('state','=','confirmed')], order='report_date ASC')
        arr_tmp = {}
        for obj in self.browse(cr, uid, obj_ids):
            for line in obj.line_ids:
                time = 0;
                complete = 0;
                if arr_tmp.has_key(line.product_id.id):
                    time = arr_tmp[line.product_id.id]['time']
                    if arr_tmp[line.product_id.id]['complete'] % 1 == 0:
                        time = time + 1
                    complete += arr_tmp[line.product_id.id]['complete']
                else:
                    time = 1
                #cong compalte
                complete += line.complete

                #search time

                time_ids = self.pool.get('hpusa3d.times').search(cr, uid, [('name', '=', time)])
                if time_ids:
                    self.pool.get('hpusa.3d.report.line').write(cr, uid, [line.id], {'_3d_design_times': time_ids[0]})
                arr_tmp[line.product_id.id] = {'time': time, 'complete': complete}

#     def create(self, cr, uid, vals, context=None):
#         res = super(hpusa_daily_report_3d, self).create(cr, uid, vals, context=context)
#         partner_id = []
#         if 'designer_id' in vals:
#             partner_id.append(self.pool.get('hr.employee').browse(cr, uid, vals['designer_id']).user_id.partner_id.id)
#         if 'invoice_manager' in vals:
#             partner_id.append(self.pool.get('res.users').browse(cr, uid, vals['invoice_manager']).partner_id.id)
#         v = {
#                 'model_obj': 'hpusa.daily.report.3d',
#                 'res_model': 'hpusa.daily.report.3d',
#                 'res_id': int(res),
#                 'partner_ids': [(6,0, partner_id) ]
#              }
#         print v
#         in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
#         self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
#         return res
#         
#     def write(self, cr, uid, ids, vals, context=None):
#         res = super(hpusa_daily_report_3d, self).write(cr, uid, ids, vals, context)
#         partner_id = 0
#         if 'designer_id' in vals:
#             if(self.pool.get('hr.employee').browse(cr, uid, vals['designer_id']).user_id):
#                 partner_id = self.pool.get('hr.employee').browse(cr, uid, vals['designer_id']).user_id.partner_id.id
#         if 'invoice_manager' in vals:
#             partner_id.append(self.pool.get('res.users').browse(cr, uid, vals['invoice_manager']).partner_id.id)
#         v = {
#                 'model_obj': 'hpusa.daily.report',
#                 'res_model': 'hpusa.daily.report',
#                 'message': 'Follower',
#                 'res_id': int(res),
#                 'partner_ids': [(6,0, partner_id) ]
#              }
#         mail_invite = self.pool.get('mail.wizard.invite')
#         context = {'default_res_model': 'hpusa.daily.report.3d', 'default_res_id': int(res)}
#         mail_invite_id = mail_invite.create(cr, uid, {'partner_ids': [(4, 17244)]}, context)
#         mail_invite.add_followers(cr, uid, [mail_invite_id])
#          
# #         in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
# #         #print [in_id]
# #         self.pool.get('mail.wizard.invite').add_followers(cr, uid, [int(in_id)])
#         return res
        
hpusa_daily_report_3d()  

class hpusa_3d_report_line(osv.osv):
    _name = 'hpusa.3d.report.line'
    def _get_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            if(obj._3d_difficulty_level):
                res[obj.id] = obj.complete * obj._3d_difficulty_level.coefficient
            else:
                res[obj.id] = 0;
        return res
    
    _columns = {
        'parent_id': fields.many2one('hpusa.daily.report.3d', 'Parent'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        '_3d_design_times': fields.many2one('hpusa3d.times','3D Design Times', required=True),
        '_3d_difficulty_level': fields.related('product_id', '_3d_difficulty_level', type="many2one", relation="hpusa3d.difficulty.level", string="3D Difficulty Level", readonly=True, track_visibility='onchange'),
        'complete': fields.float('Complete'), 
        'point': fields.function(_get_point,type='float',string='Point', track_visibility='onchange'),
    }     
    def create(self, cr, uid, vals, context=None):
        if vals['complete'] > 1 or vals['complete'] < 0:
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1'))
        self.pool.get('product.product').write(cr, uid, [vals['product_id']], {'_3d_design_times': vals['_3d_design_times']})
        res = super(hpusa_3d_report_line, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if 'complete' in vals and (vals['complete'] > 1 or vals['complete'] < 0):
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1'))

        if '_3d_design_times' in vals:
            if 'product_id' in vals:
                self.pool.get('product.product').write(cr, uid, [vals['product_id']], {'_3d_design_times': vals['_3d_design_times']})
            else:
                product_id = self.browse(cr, uid, ids[0]).product_id.id
                self.pool.get('product.product').write(cr, uid, [product_id], {'_3d_design_times': vals['_3d_design_times']})
        res = super(hpusa_3d_report_line, self).write(cr, uid, ids, vals, context)

hpusa_3d_report_line()

class hpusa_daily_report_casting(osv.osv):
    _name = "hpusa.daily.report.casting"
    _table = "hpusa_daily_report"
    _inherit = "hpusa.daily.report" 
    def _get_total_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            sum = 0.0
            for line in  obj.line_ids:
                sum += line.point
            res[obj.id] = sum
        return res
    
    _columns = {
        'total_point': fields.function(_get_total_point,type='float',string='Total point', track_visibility='onchange'),
        'manager_id': fields.many2one('hr.employee', 'Manager',required=True),
        'line_ids': fields.one2many('hpusa.casting.report.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': 'casting',
    }  

    def action_update(self, cr, uid, ids, context):
        obj_ids = self.search(cr, uid, [('state','=','confirmed')], order='report_date ASC')
        arr_tmp = {}
        for obj in self.browse(cr, uid, obj_ids):
            for line in obj.line_ids:
                time = 0;
                complete = 0;
                if arr_tmp.has_key(line.product_id.id):
                    time = arr_tmp[line.product_id.id]['time']
                    if arr_tmp[line.product_id.id]['complete'] % 1 == 0:
                        time = time + 1
                    complete += arr_tmp[line.product_id.id]['complete']
                else:
                    time = 1
                #cong compalte
                complete += line.complete

                #search time

                time_ids = self.pool.get('hpusa.casting.times').search(cr, uid, [('name', '=', time)])
                if time_ids:
                    self.pool.get('hpusa.casting.report.line').write(cr, uid, [line.id], {'casting_times': time_ids[0]})
                arr_tmp[line.product_id.id] = {'time': time, 'complete': complete}
                
hpusa_daily_report_casting()

class hpusa_casting_report_line(osv.osv):
    _name = 'hpusa.casting.report.line' 
    def _get_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            if(obj.product_id.casting_type == 'gold'):
                coefficient = 0
                if(obj.casting_times):
                    coefficient = obj.casting_times.coefficient_gold
                res[obj.id] = obj.complete * coefficient;
            else:
                coefficient = 0
                if(obj.casting_times):
                    coefficient = obj.casting_times.coefficient_pt
                res[obj.id] = obj.complete * coefficient;
        return res
    
    _columns = {
        'parent_id': fields.many2one('hpusa.daily.report.casting','Parent'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'casting_times':  fields.many2one('hpusa.casting.times','Casting Times', required=True),
        'worker': fields.many2one('hr.employee', 'Worker'),
        'complete': fields.float('Complete'), 
        'point': fields.function(_get_point,type='float',string='Point', track_visibility='onchange'),
    }
    def create(self, cr, uid, vals, context=None):
        if vals['complete'] > 1 or vals['complete'] < 0:
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1'))
        self.pool.get('product.product').write(cr, uid, [vals['product_id']], {'casting_times': vals['casting_times']})
        res = super(hpusa_casting_report_line, self).create(cr, uid, vals, context=context)
        return res    

    def write(self, cr, uid, ids, vals, context=None):
        if 'complete' in vals and (vals['complete'] > 1 or vals['complete'] < 0):
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1'))
        if 'casting_times' in vals:
            if 'product_id' in vals:
                self.pool.get('product.product').write(cr, uid, [vals['product_id']], {'casting_times': vals['casting_times']})
            else:
                product_id = self.browse(cr, uid, ids[0]).product_id.id
                self.pool.get('product.product').write(cr, uid, [product_id], {'casting_times': vals['casting_times']})
        res = super(hpusa_casting_report_line, self).write(cr, uid, ids, vals, context)
          
hpusa_casting_report_line()

class hpusa_daily_report_assembling(osv.osv):
    _name = "hpusa.daily.report.assembling"
    _table = "hpusa_daily_report"
    _inherit = "hpusa.daily.report" 
    def _get_total_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            sum = 0.0
            for line in  obj.line_ids:
                sum += line.point
            res[obj.id] = sum
        return res
    
    _columns = {
        'total_point': fields.function(_get_total_point,type='float',string='Total point', track_visibility='onchange'),
        'line_ids': fields.one2many('hpusa.assembling.report.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': 'assembling',
    }

hpusa_daily_report_assembling()

class hpusa_assembling_report_line(osv.osv):
    _name = 'hpusa.assembling.report.line'
    def _get_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            coefficient = 0
            if(obj.product_id.ass_difficulty_level):
                coefficient = obj.product_id.ass_difficulty_level.coefficient;
            res[obj.id] = obj.complete * coefficient;
        return res
    
    _columns = {
        'parent_id': fields.many2one('hpusa.daily.report.assembling','Parent'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'worker': fields.many2one('hr.employee', 'Worker'),
        'level': fields.related('product_id', 'ass_difficulty_level', type="many2one", relation="hpusa.ass.difficulty.level", string="Assembling Difficulty Lv", readonly=True, track_visibility='onchange'),
        'complete': fields.float('Complete'), 
        'point': fields.function(_get_point,type='float',string='Point', track_visibility='onchange'),
    }

    def create(self, cr, uid, vals, context=None):
        if vals['complete'] > 1 or vals['complete'] < 0:
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1'))
        res = super(hpusa_casting_report_line, self).create(cr, uid, vals, context=context)
        return res    

    def write(self, cr, uid, ids, vals, context=None):
        if 'complete' in vals and (vals['complete'] > 1 or vals['complete'] < 0):
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1')) 
        res = super(hpusa_casting_report_line, self).write(cr, uid, ids, vals, context)
        return res     
hpusa_assembling_report_line()

class hpusa_daily_report_setting(osv.osv):
    _name = "hpusa.daily.report.setting"
    _table = "hpusa_daily_report"
    _inherit = "hpusa.daily.report" 
    def _get_total_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            sum = 0.0
            for line in  obj.line_ids:
                sum += line.point
            res[obj.id] = sum
        return res
    
    _columns = {
        'total_point': fields.function(_get_total_point,type='float',string='Total point', track_visibility='onchange'),
        'manager_id': fields.many2one('hr.employee', 'Manager',required=True),
        'line_ids': fields.one2many('hpusa.setting.report.line', 'parent_id','Lines'),
    }
    _defaults = {
        'type': 'setting',
    }
hpusa_daily_report_setting()

class hpusa_setting_report_line(osv.osv):
    _name = 'hpusa.setting.report.line'
    def _get_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            coefficient = 0
            if(obj.product_id.setting_difficulty_level):
                coefficient = obj.product_id.setting_difficulty_level.coefficient
            res[obj.id] = obj.complete * coefficient;
        return res
    
    _columns = {
        'parent_id': fields.many2one('hpusa.daily.report.setting','Parent'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'worker': fields.many2one('hr.employee', 'Worker'),
        'level': fields.related('product_id', 'setting_difficulty_level', type="many2one", relation="hpusa.setting.difficulty.level", string="Setting Difficulty Lv", readonly=True, track_visibility='onchange'),
        'complete': fields.float('Complete'), 
        'point': fields.function(_get_point,type='float',string='Point', track_visibility='onchange'),
    }  

    def create(self, cr, uid, vals, context=None):
        if vals['complete'] > 1 or vals['complete'] < 0:
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1'))
        res = super(hpusa_casting_report_line, self).create(cr, uid, vals, context=context)
        return res    

    def write(self, cr, uid, ids, vals, context=None):
        if 'complete' in vals and (vals['complete'] > 1 or vals['complete'] < 0):
            raise osv.except_osv(('Wanning'),('Please ipnut complete from 0 to 1')) 
        res = super(hpusa_casting_report_line, self).write(cr, uid, ids, vals, context)
        return res      
hpusa_setting_report_line()





