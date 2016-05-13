# -*- coding: utf-8 -*-
from openerp import netsvc
import time

from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.tools.misc import attrgetter
import openerp.addons.decimal_precision as dp

class wizard_configuration_parameters(osv.osv_memory):
    _name="wizard.configuration.parameters"
    
    def _models_field_get(self, cr, uid, field_key, field_value, context=None):
        get = attrgetter(field_key, field_value)
        obj = self.pool.get('ir.model.fields')
        ids = obj.search(cr, uid, [('view_load','=',1)], context=context)
        res = set()
        for o in obj.browse(cr, uid, ids, context=context):
            res.add(get(o))
        return list(res)

    def _models_get(self, cr, uid, context=None):
        return self._models_field_get(cr, uid, 'model', 'model_id.name', context)

    def _models_get2(self, cr, uid, context=None):
        return self._models_field_get(cr, uid, 'relation', 'relation', context)
    
    _columns={
            'name': fields.char('Name', size=128, select=1),
            'model_id': fields.many2one('ir.model', 'Model'),
            'fields_id': fields.many2one('ir.model.fields', 'Field', ondelete='cascade', required=True, select=1),
            'value_reference': fields.reference('Value', selection=_models_get2, size=128),
            'type': fields.selection([('update','Updates'),('default_get','Default Gets')],'Type', required=True),
            'company_id': fields.many2one('res.company', 'Company', select=1),
              }
    
    _defaults = {
        'type': 'update',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'wizard.configuration.parameters', context=c),
        }
    
    def onchange_fields_id(self, cr, uid, ids, fields_id,context=None):
        if not fields_id:
            return {'value': {'name': False}}
        
        fields = self.pool.get('ir.model.fields').browse(cr, uid, fields_id)
        return {'value': {'name': fields.name or False}}
    
    def button_make(self, cr, uid, ids, context=None):
        ir_property_pool = self.pool.get("ir.property")
        for wizard in self.browse(cr, uid, ids):
            value_reference = '%s,%d' % (wizard.value_reference._name, wizard.value_reference.id)
            if wizard.type == 'update':
                ir_ids = ir_property_pool.search(cr, uid, [('company_id','=',wizard.company_id.id),('fields_id','=',wizard.fields_id.id)])
                for ir_property in ir_property_pool.browse(cr, uid, ir_ids):
                    ir_property_pool.write(cr, uid, ir_property.id,{'value_reference': value_reference})
            else:
                cr.execute('''DELETE FROM ir_property WHERE company_id = %s AND fields_id = %s AND res_id is NULL  
                '''%(wizard.company_id.id or False, wizard.fields_id.id or False))
                cr.execute('commit;')
                vars = {'name': wizard.name or False, 'fields_id': wizard.fields_id.id or False, 'company_id': wizard.company_id.id or False,
                        'type': wizard.fields_id.ttype or False,'value_reference': value_reference or False}
                ir_property_pool.create(cr, uid, vars)
        return True
                
wizard_configuration_parameters()