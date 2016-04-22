'''
Created on Aug 12, 2015

@author: Intern ERP Long
'''
from dateutil import relativedelta
import time
from datetime import datetime
from datetime import timedelta
from openerp.osv import fields, osv
import locale
from openerp.netsvc import DEFAULT
from pychart.line_style import default
from decimal import Context
from openid.consumer.discover import arrangeByType
locale.setlocale(locale.LC_ALL,"")
import sys;
reload(sys);
from openerp.addons.pxgo_openoffice_reports import openoffice_report
sys.setdefaultencoding("utf8")

#sys.setdefaultencoding("utf8")

class hpusa_reportddp_wizard(osv.osv):
    _name  = 'hpusa.reportddp'
    
    _description = "Wip Report"
     
    _columns = {
            'from_date': fields.date('From Date','date',require = True),
            'to_date': fields.date('To Date','date',require = True),
            'so_id': fields.many2many('sale.order', '', 'id', 'name', "Sale Order" ),
            'work_center': fields.many2one('mrp.workcenter', 'Work Center') ,
            'status': fields.selection([('Draft','Draft'),('Cancelled','Cancelled'),('Waiting Material', 'Waiting Material'),('Pending','Pending'),('Inprogress', 'Inprogress'),('Waiting Director','Waiting Director'),('Done','Done')], "Status" ,readonly=False,track_visibility='onchange') ,
            'worker': fields.many2one('hr.employee', 'Worker') ,
            'content':fields.html('Content',help='Automatically sanitized HTML contents',store=True)  ,
            'state':fields.selection([('get', 'get'),('choose','choose')]),
            'company_id': fields.many2many('res.company','company_rel','ddp_id_rel','ddp_company_rel','Company'),
            'check_order_date':fields.boolean('Date Order'),
            'check_pickup_date': fields.boolean('Pickup Date'),
            'check_due_date': fields.boolean('Due Date'),                                   
     }
    _defaults={  
              'check_order_date':True,
              'from_date': lambda *a: time.strftime('%Y-%m-01'),
              'to_date': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
              'state':'choose',
    }
    
    def action_export(self, cr, uid, ids, context=None):
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['from_date','to_date','company_id','work_center','status','worker','customer_id'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'hpusa.reportddp'
        type = context.get('type_', '')
        this = self.browse(cr, uid,ids,context =None)[0]
        x = 0
        sid = ''
        if this.so_id:
                sid += '('
                for item in this.so_id:
                    x = x+1
                    so_id =item.id
                    if x == len(this.so_id):
                        sid += str(so_id)
                    else:
                        sid += str(so_id)  + ','
                sid += ')'
        if type == 'data':
            datas['line']  = self.get_all_data(cr, uid, res['from_date'], res['to_date'], sid, res['work_center'], res['status'], this.worker.id,this.company_id,this.check_order_date,this.check_pickup_date,this.check_due_date, context=None)
            datas['line1']  = self.get_all_data_detail(cr, uid, res['from_date'], res['to_date'], sid, res['work_center'], res['status'], this.worker.id,this.company_id,this.check_order_date,this.check_pickup_date,this.check_due_date, context=None)
            datas['line2']  = self.get_so_detail(cr, uid, res['from_date'], res['to_date'],this.company_id, context=None)
            return {
                    'type'          : 'ir.actions.report.xml',
                    'report_name'   : 'export_data_wip_sumary',
                    'datas'         : datas,
                    }
        else:
            datas['line']  = self.get_all_data(cr, uid, res['from_date'], res['to_date'], sid, res['work_center'], res['status'], this.worker.id,this.company_id,this.check_order_date,this.check_pickup_date,this.check_due_date, context=None)
            datas['line1']  = self.get_all_data_detail(cr, uid, res['from_date'], res['to_date'], sid, res['work_center'], res['status'], this.worker.id,this.company_id,this.check_order_date,this.check_pickup_date,this.check_due_date, context=None)
            datas['line2']  = self.get_so_detail(cr, uid, res['from_date'], res['to_date'],this.company_id, context=None)
            return {
                    'type'          : 'ir.actions.report.xml',
                    'report_name'   : 'export_data_wip_sumary_manager',
                    'datas'         : datas,
                    }
            
        
          
    def get_state (self,cr,uid,status, context=None):
        if status :
            if status == 'draft':
                return 'Draft'
            elif status == 'cancel':
                return 'Cancelled'
            elif status == 'confirmed':
                return  'Waiting Material'
            elif status == 'pause':
                return 'Pending'
            elif status == 'startworking':
                return 'In Progress'
            elif status == 'waiting_director':
                return 'Waiting Director'
            elif status == 'done':
                return 'Done'
    
    def get_all_data(self ,cr, uid,from_date,to_date ,so_id,work_center,status,worker,company_id,check_order_date,check_pickup_date,check_due_date,context=None):
            #self.get_all_data_detail(cr, uid, from_date, to_date, so_id, work_center, status, worker,company_id,check_order_date,check_pickup_date,check_due_date, context=None)
            arr =[]
            sql =''
            str_query =''
            sql_get_company=''
            company_ids = []
            so_query='  '    
                 
            if check_order_date==True:
                str_query += ''' and so.date_order >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                str_query += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
                sql_get_company+=''' where so.date_order >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                sql_get_company += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
            if check_pickup_date==True: 
                str_query += ''' and so.x_pickup_date >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                str_query += ''' and so.x_pickup_date <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
                sql_get_company += ''' where so.x_pickup_date >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                sql_get_company += ''' and so.x_pickup_date <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
            if check_due_date==True:
                str_query += ''' and mp.mo_date >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                str_query += ''' and mp.mo_date <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                so_query += ''' and mp.mo_date >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                so_query += ''' and mp.mo_date <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                sql_get_company += ''' where so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                #sql_get_company += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)    
            
            if company_id:
                for id in company_id:
                    company_ids.append(id.id)
            else:
                sql_get='''select distinct(company_id) as company_id from sale_order so %s'''%(sql_get_company)
                
                cr.execute(sql_get) 
                result = cr.dictfetchall() 
                for item in result:
                    company_ids.append(item['company_id'])            
                                        
                
            if so_id:
                str_query += ''' and mp.so_id in %s '''%(so_id)
                so_query+='''and mp.so_id in %s '''%(so_id)
            else:
                so_ids=[]
                sql_get='''select distinct(id) as so_id from sale_order so %s'''%(sql_get_company)
                cr.execute(sql_get)
                result = cr.dictfetchall() 
                for item in result:
                    so_ids.append(item['so_id'])
                if(len(result)>=1):
                    so_id=str(so_ids)
                    so_id=so_id.replace('[', '(')
                    so_id = so_id.replace(']',')')
                    str_query += ''' and mp.so_id in %s '''%(so_id)
                    so_query+='''and mp.so_id in %s '''%(so_id)    
                
            if work_center:
                work_center_name  = self.pool.get('mrp.workcenter').browse(cr, uid, work_center).name
                str_query += '''and mp.wo_view = '%s' '''%(work_center_name)
            if status :
                str_query += '''and mp.state_view = '%s' '''% (status)
            if worker:
                str_query += ''' and mp.employee_id = %s'''%(str(worker))
            list_workcenter= ['3D Design','Waxmodeling','Casting','Assembling','Setting','Polishing']
            
            for co_id in company_ids:
                
                company_query=''' and so.company_id = %s'''%(co_id)
                company_name = self.pool.get('res.company').browse(cr,uid,co_id,context=None).name
                total_product=0
                first =True
                index=0
                for workcenter in list_workcenter:
                                      
                    sql ='''
                        select mp.wo_view  
                        ,coalesce( max(tab1.count),0) as draft
                        ,coalesce( max(tab2.count),0) as waiting_material
                        ,coalesce( max(tab3.count),0) as pending 
                        ,coalesce( max(tab4.count),0) as inprogress
                        ,coalesce( max(tab5.count),0) as waiting_director
                        ,coalesce( max(tab6.count),0) as done
                        ,coalesce( max(tab7.count),0) as cancelled
                        ,coalesce( max(tab8.count),0) as sum
                        from mrp_production mp
                        -- Draft
                        left join
                        (
                        select 
                            mp.wo_view
                            ,coalesce( count(*),0)  as count
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id
                            and state_view ='Draft' 
                            %s
                            %s
                            group by mp.wo_view,mp.state_view
                        ) as tab1 on ( tab1.wo_view=mp.wo_view)
                          -- Waiting Material
                        left join
                        (
                        select
                mp.wo_view
                            ,coalesce( count(*),0)  as count
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id
                            and state_view ='Waiting Material' 
                            %s
                            %s
                            group by mp.wo_view,mp.state_view
                        ) as tab2 on ( tab2.wo_view=mp.wo_view)
            -- Pending
                         left join
                        (
                        select
                mp.wo_view
                            ,coalesce( count(*),0)  as count
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id
                            and state_view ='Pending' 
                            %s
                            %s
                            group by mp.wo_view,mp.state_view
                        ) as tab3 on ( tab3.wo_view=mp.wo_view)
                        -- Inprogress
                        left join
                        (
                            select
                mp.wo_view
                            ,coalesce( count(*),0)  as count
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id
                            and state_view ='Inprogress' 
                            %s
                            %s
                            group by mp.wo_view,mp.state_view
                        ) as tab4 on ( tab4.wo_view=mp.wo_view)
                        --Waiting Director
                        left join
                        (
                        select
                mp.wo_view
                            ,coalesce( count(*),0)  as count
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id
                            and state_view ='Waiting Director' 
                            %s
                            %s
                            group by mp.wo_view,mp.state_view
                        ) as tab5 on ( tab5.wo_view=mp.wo_view)
                        -- Done
                        left join
                        (
                            select
                mp.wo_view'''%(workcenter,so_query,company_query,workcenter,so_query,company_query,workcenter,so_query,company_query,workcenter,so_query,company_query,workcenter,so_query,company_query)
                    
                    if workcenter=='Polishing':
                        sql += ",0  as count"
                    else:
                        sql += ",coalesce( count(*),0)  as count"   
                    
                    sql+='''
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id   
                            and state_view ='Done'                         
                            %s
                            %s
                            group by mp.wo_view,mp.state_view
                        ) as tab6 on ( tab6.wo_view=mp.wo_view)
                        -- Cancelled
                        left join
                        (
                            select
                            mp.wo_view
                            ,coalesce( count(*),0)  as count
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id
                            and state_view ='Cancelled' 
                            %s
                            %s
                            group by mp.wo_view,mp.state_view
                        ) as tab7 on ( tab7.wo_view=mp.wo_view)
                        -- Total
                        left join
                        (
                            select
                            mp.wo_view   
                            ,coalesce( count(*),0)  as count
                            from mrp_production mp
                            ,sale_order so
                            where wo_view='%s'
                            and so.id = mp.so_id'''%(workcenter,so_query,company_query,workcenter,so_query,company_query,workcenter)
                    if workcenter=='Polishing':
                        sql += " and state_view <>'Done'  "
                    else:
                        sql += "  "
                    sql+='''             
                            %s
                            %s
                            group by mp.wo_view
                        ) as tab8 on ( tab8.wo_view=mp.wo_view)
                        left join sale_order as so on(so.id = mp.so_id)
                        where mp.wo_view= '%s'
                        %s
                        and so.company_id = %s
                        group by mp.wo_view  ;

                                '''%(so_query,company_query,workcenter,str_query,co_id)            
                    
                    cr.execute(sql)
                    print sql 
                    result = cr.dictfetchall() 
                    for item in result:
                            
                        print 'ok'
                        arr.append({
                                    'company_id':company_name,
                                    'total':0,
                                    'work_order':workcenter,
                                    'draft':item['draft'],
                                    'waiting_material':item['waiting_material'],
                                    'pending':item['pending'],
                                    'inprogress':item['inprogress'],
                                    'waiting_director':item['waiting_director'],
                                    'done':item['done'],
                                    'cancel':item['cancelled'],
                                    'sum':item['sum'],                    
                                    })
                        if first==True:
                            index= len(arr)-1;
                            first=False
                            
                        company_name=''
                        total_product+=float(item['sum'] or 0)
                        arr[index]['total']=total_product
            
        
            return arr
    
    def get_all_data_detail(self ,cr, uid,from_date,to_date ,so_id,work_center,status,worker,company_id,check_order_date,check_pickup_date,check_due_date,context=None):
            arr =[]
            sql =''
            str_query =''
            sql_get_company=''
            company_ids = []
                
                 
            if check_order_date==True:
                str_query += ''' and so.date_order >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                str_query += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
                sql_get_company+=''' where so.date_order >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                sql_get_company += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
            if check_pickup_date==True: 
                str_query += ''' and so.x_pickup_date >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                str_query += ''' and so.x_pickup_date <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
                sql_get_company += ''' where so.x_pickup_date >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                sql_get_company += ''' and so.x_pickup_date <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
            if check_due_date==True:
                str_query += ''' and mp.mo_date >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                str_query += ''' and mp.mo_date <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
                
                sql_get_company += ''' where so.date_order >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
                sql_get_company += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)    
            
            if company_id:
                for id in company_id:
                    company_ids.append(id.id)
            else:
                sql_get='''select distinct(company_id) as company_id from sale_order so %s'''%(sql_get_company)
                
                cr.execute(sql_get) 
                result = cr.dictfetchall() 
                for item in result:
                    company_ids.append(item['company_id'])            
                                        
                
            if so_id:
                str_query += ''' and mp.so_id in %s '''%(so_id)
            if work_center:
                work_center_name  = self.pool.get('mrp.workcenter').browse(cr, uid, work_center).name
                str_query += '''and mp.wo_view = '%s' '''%(work_center_name)
            if status :
                str_query += '''and mp.state_view = '%s' '''% (status)
            if worker:
                str_query += ''' and mp.employee_id = %s'''%(str(worker))
                
                
            list_workcenter= ['3D Design','Waxmodeling','Casting','Assembling','Setting','Polishing']
            
            sequence=0
            
            for co_id in company_ids:
                
                company_name = self.pool.get('res.company').browse(cr,uid,co_id,context=None).name
                if work_center:                    
                    sql ='''
                            select 
                            so.company_id
                            ,so.id as so_id
                            ,tab1.customer_id 
                            ,tab1.name
                            ,tab1.sale_name
                            ,tab1.x_pickup_date
                            ,tab1.x_due_date
                            ,tab1.date_order
                            ,pp.name_template as product_name
                            ,mp.name as mo_name
                            ,mp.product_qty
                            ,mp.wo_view
                            ,mp.state_view
                            ,he.name_related as employee
                            ,mp.mo_date
                            ,mp.description
                            ,re.name as customer_name
                            , re.phone 
                            , re.mobile
                            , cr.name as crm_name
                            from mrp_production mp
                            left join sale_order as so on(mp.so_id=so.id)
                            left join res_partner as re on (re.id = so.partner_id)
                            left join crm_vip_program as cr on (cr.id = re.vip_program_id)
                            -- sale order
                            left join 
                            (select 
                                so.id as id
                                , so.name as name
                                , so.x_pickup_date
                                , so.x_due_date
                                , rp.name as customer_id
                                , pn.name as sale_name
                                , so.date_order as date_order
                                from 
                                sale_order as so
                                ,res_partner rp
                                ,res_users ru
                                ,res_partner pn
                                where rp.id = so.partner_id
                                and ru.id = so.user_id
                                and ru.partner_id = pn.id
                            )
                            as tab1 on(tab1.id = mp.so_id)
                            -- product
                            left join 
                            product_product as pp on(pp.id = mp.product_id) 
                            left join hr_employee as he on(he.id = mp.employee_id)
                            where so.id= mp.so_id
                            %s
                            and so.company_id=%s
                            and state_view <>'Done'
                            and  wo_view <> 'Polishing' 
                            order by  so.company_id,tab1.name,tab1.date_order;
                                    '''%(str_query,co_id)            
                    cr.execute(sql)
                    print sql 
                    result = cr.dictfetchall() 
                    for item in result:
                        arr.append({                                        
                                    'sequence':sequence,
                                    'company_id':company_name,
                                    'customer_name': item['customer_name'],
                                    'mobile_phone':str(item['phone'])+ ','+str(item['mobile']),
                                    'crm_name' : item['crm_name'],
                                    'customer_name':item['customer_id'],
                                    'so_id':item['name'],
                                    'mo_name': item['mo_name'],
                                    'date_order':item['date_order'],
                                    'salesperson':item['sale_name'],
                                    'pickup_date':item['x_pickup_date'],
                                    'product_name':item['product_name'],
                                    'qty_order':item['product_qty'],
                                    'work_center':item['wo_view'],
                                    'status':item['state_view'],
                                    'worker':item['employee'],
                                    'due_date':item['mo_date'],
                                    'remark':item['description'] ,
                                    'so_id':  item['so_id'] ,           
                                })
                        sequence+=1
                else: 
                    for workcenter in list_workcenter:
                                          
                        sql ='''
                            select 
                            so.company_id
                            ,tab1.customer_id 
                            ,so.id as so_id
                            ,tab1.name 
                            ,tab1.sale_name
                            ,tab1.date_order
                            ,tab1.x_pickup_date
                            ,tab1.x_due_date
                            ,pp.name_template as product_name
                            ,mp.name as mo_name
                            ,mp.product_qty
                            ,mp.wo_view
                            ,mp.state_view
                            ,he.name_related as employee
                            ,mp.mo_date
                            ,mp.description
                            ,re.name as customer_name
                            , re.phone 
                            , re.mobile
                            , cr.name as crm_name
                            from mrp_production mp
                            left join sale_order as so on(mp.so_id=so.id)
                            left join res_partner as re on (re.id = so.partner_id)
                            left join crm_vip_program as cr on (cr.id = re.vip_program_id)
                            -- sale order
                            left join 
                            (select 
                                so.id as id
                                , so.name as name
                                , so.x_pickup_date
                                , so.x_due_date
                                , rp.name as customer_id
                                , pn.name as sale_name
                                , so.date_order as date_order
                                from 
                                sale_order as so
                                ,res_partner rp
                                ,res_users ru
                                ,res_partner pn
                                where rp.id = so.partner_id
                                and ru.id = so.user_id
                                and ru.partner_id = pn.id
                            )
                            as tab1 on(tab1.id = mp.so_id)
                            -- product
                            left join 
                            product_product as pp on(pp.id = mp.product_id) 
                            left join hr_employee as he on(he.id = mp.employee_id)
                            where so.id= mp.so_id
                            %s
                            and so.company_id=%s
                            and mp.wo_view='%s'
                             '''%(str_query,co_id,workcenter)
                        if workcenter =='Polishing':
                            sql+="and state_view <>'Done' "
                        sql+=   '''order by  so.company_id,tab1.name,tab1.date_order;
                                    '''
                        cr.execute(sql)
                        print sql 
                        result = cr.dictfetchall() 
                        for item in result:
                            arr.append({
                                    'sequence':sequence,
                                    'company_id':company_name,
                                    'customer_name': item['customer_name'],
                                    'mobile_phone':str(item['phone'])+ ','+str(item['mobile']),
                                    'crm_name' : item['crm_name'],
                                    'customer_name':item['customer_id'],
                                    'so_id':item['name'],
                                    'mo_name': item['mo_name'],
                                    'date_order':item['date_order'],
                                    'salesperson':item['sale_name'],
                                    'pickup_date':item['x_pickup_date'],
                                    'product_name':item['product_name'],
                                    'qty_order':item['product_qty'],
                                    'work_center':item['wo_view'],
                                    'status':item['state_view'],
                                    'worker':item['employee'],
                                    'due_date':item['mo_date'],
                                    'remark':item['description'],
                                    'so_id':  item['so_id'] ,                   
                                        })
                            sequence+=1
            print arr                    
            return arr
    def view_rp(self,cr,uid,ids,context= None):
        this = self.browse(cr, uid,ids,context =None)[0]
        from_date = this.from_date
        to_date= this.to_date
        x = 0
        sid = ''
        if this.so_id:
            sid += '('
            for item in this.so_id:
                x = x+1
                so_id =item.id
                if x == len(this.so_id):
                    sid += str(so_id)
                else:
                    sid += str(so_id)  + ','
            sid += ')'
                      
        work_center = this.work_center.id
        status = this.status
        worker = this.worker.id
        total = 0
        arr = self.get_all_data(cr, uid, from_date, to_date, sid, work_center, status, worker,this.company_id,this.check_order_date,this.check_pickup_date,this.check_due_date, context=None)
        html = ''
        if arr:
            html += '<span contenteditable="false">'\
                    '<h1  style = "text-align:center"> WORK IN PROCESS(WIP) </h1>'\
                    '<table  width="800px"  class ="tables" style = "border : 1px solid #999 ; border-collapse: collapse">'\
                    '<thead class = "theads">'\
                      '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">COMPANY</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">TOTAL PRODUCT</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white">WORKCENTER</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >DRAFT</th>'\
                          '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >WAITING MATERIAL</th>'\
                            '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >PENDING</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >INPROGRESS</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >QC</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >DONE</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >CANCEL</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: center ; color : white" >SUM</th>'\
                      '</tr>' \
                    '</thead>'\
                    '<tbody>'
            for  i in arr:
                
                
                html += '<tr class = "trs">'
                if i['company_id']:
                    
                    html+='<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i["company_id"])+'</td>'     
                else :
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'		            
                if i["total"]:
                    html+='<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i["total"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'   
                if i["work_order"]:
                    html+='<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left">'+ str(i["work_order"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'               
                if i["draft"]:
                    html+='<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i["draft"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'    
                    
                if i["waiting_material"]:
                    html+='<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i["waiting_material"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'    
                if i["pending"]:
                    html+='<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i["pending"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'    
                    
                if i["inprogress"]:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i["inprogress"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'                
                if i["waiting_director"]:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i["waiting_director"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'
                if i["done"]:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+ str(i["done"])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'
                if i['cancel']:
                    html += '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: right">'+str(i['cancel'])+'</td>'
                else:
                    html += '<td class ="tds" style = "border : 1px solid #999" ; border-collapse: collapse ; text-align: left"></td>'
                if ["sum"]:
                    html+= '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse  ; text-align: right">'+str(i["sum"])+'</td>'
                    total+= i["sum"]
                else:
                    html+= '<td class ="tds" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left"></td>'
               
                html+='</tr>'
            html += '</tbody>'\
                    '<footer>'\
                    '<tr>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td></td>'\
                    '<td>Total :</td>'\
                    '<td style="text-align:right">'+str(total)+'</td>'\
                    '</tr>'\
                    '</footer>'\
                    '</table>'\
                    '</span>'
        else:
            html += '<span contenteditable="false">'\
            '<table id ="tb" width="800px"  class ="tables" style ="align: center">'\
                    '<thead class = "theads">'\
                      '<tr class = "trs" style="background-color: rgb(238, 76, 140) ; text-align: center" >'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white">Sale Order</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white">Name MO</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white">Manufacturing Date</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white" >Product Code</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white" >Product Namer</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white" >WorkCenter</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white" >Work Order Status</th>'\
                        '<th class = "ths" style = "border : 1px solid #999 ; border-collapse: collapse ; text-align: left ; color : white" >Worker</th>'\
                      '</tr>' \
                    '</thead>'\
                    '<tbody>'\
                    '</tbody>'\
                    '</table>'\
                    '</span>'
        
        #print str(html)
        
        
        self.write(cr, uid,ids, {'state': 'get',
                                    'content':str(html) }, context=context)
        cr.commit()
        
        return  {
             'type': 'ir.actions.act_window',
             'res_model': 'hpusa.reportddp',
             'view_mode': 'form',
             'view_type': 'form',
             'res_id': this.id,
             'views': [(False, 'form')],
             'target': 'new',
         }
    
    def onchange_order_date(self,cr,uid,ids,check_order_date ,contxt=None):
        v = {}
        if check_order_date==True:
            
            v['check_pickup_date'] = False
            v['check_due_date'] = False
        return {'value': v} 
    
    def onchange_check_pickup_date(self, cr, uid, ids, check_pickup_date, context=None):
        v = {}
        if check_pickup_date==True:
            
            v['check_order_date'] = False
            v['check_due_date'] = False
        return {'value': v}
    
    def onchange_check_due_date(self, cr, uid, ids, check_due_date, context=None):

        v = {}
        if check_due_date==True:
            
            v['check_order_date'] = False
            v['check_pickup_date'] = False
        return {'value': v}
    
    def get_so_detail (self ,cr, uid,from_date,to_date ,company_id,context=None):
        arr = []
        so_ids = []
        sale_order = []
        str_query =''
        sql_get_company=''
        company_ids = []
        str_query += ''' and so.date_order >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
        str_query += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
        sql_get_company+=''' where so.date_order >= to_date('%s','YYYY-MM-DD')  '''%(from_date)
        sql_get_company += ''' and so.date_order <= to_date('%s','YYYY-MM-DD')  '''%(to_date)
        sql_mo = '''  select distinct(mo.so_id) from mrp_production mo where mo.so_id is not null 
        and mo.mo_date >= to_date('%s','YYYY-MM-DD') and  mo.mo_date <= to_date('%s','YYYY-MM-DD')
        '''%(from_date,to_date) 
        cr.execute(sql_mo)
        result1 = cr.dictfetchall() 
        for index in result1:
            arr.append(index)
        if company_id:
                for id in company_id:
                    company_ids.append(id.id)
        else:
                sql_get='''select distinct(company_id) as company_id from sale_order so %s'''%(sql_get_company)
                cr.execute(sql_get) 
                result = cr.dictfetchall() 
                for item in result:
                    company_ids.append(item['company_id'])   
        if arr:
            for i in arr:
                so_ids.append(i['so_id'])
        if so_ids:
            so_id =  str(so_ids).replace('[', '(')
            so_id = str(so_id).replace(']', ')') 
        sequence=0
        for co_id in company_ids:
            company_name = self.pool.get('res.company').browse(cr,uid,co_id,context=None).name
            sale_order.append({'company':company_name,
                                  'no':'',
                                  'so_name': '',
                                  'customer':'',
                                  'state':'',
                                  'sale_name':'',
                                  'date_order': '',
                                  'date_confirm':'',
                                  'total_product':'',
                                  })
            if so_id:
                sql =''' select so.id, so.name , so.date_order, rp.name as customer , so.state, so.date_confirm, pn.name as sale_name, count(sol.id) as total_product
                            from sale_order as so
                                ,res_partner rp
                                ,res_users ru
                                ,res_partner pn
                                 ,sale_order_line sol
                                where rp.id = so.partner_id
                                and ru.id = so.user_id
                                and ru.partner_id = pn.id
                                and sol.order_id = so.id
                                and so.sale_order_type = 'customize'
                                and so.id not in %s
                                %s
                                and so.company_id = %s
                                group by  so.id, so.name , so.date_order,rp.name,so.state, so.date_confirm, pn.name '''%(so_id ,str_query,co_id)         
                                   
                cr.execute(sql)
                print sql 
                result = cr.dictfetchall() 
            total_product_company = 0
            for item in result:
                sequence = sequence + 1
                total_product_company = total_product_company + item['total_product']
                sale_order.append({'company':'',
                                  'no':sequence,
                                  'so_name': item['name'],
                                  'customer':item['customer'],
                                  'state':item['state'],
                                  'sale_name':item['sale_name'],
                                  'date_order': item['date_order'],
                                  'date_confirm':item['date_confirm'],
                                  'total_product':item['total_product'],
                                  })
            sale_order.append({'company':'',
                                  'no':'',
                                  'so_name': '',
                                  'customer':'',
                                  'state':'',
                                  'sale_name':'',
                                  'date_order': '',
                                  'date_confirm':'Total',
                                  'total_product':total_product_company,
                                  })
        return sale_order
                
hpusa_reportddp_wizard()

openoffice_report.openoffice_report(
    'report.export_data_wip_sumary',
    'hpusa.reportddp',
    parser=hpusa_reportddp_wizard
)
openoffice_report.openoffice_report(
    'report.export_data_wip_sumary_manager',
    'hpusa.reportddp',
    parser=hpusa_reportddp_wizard
)
# hpusa 08-07-2015
