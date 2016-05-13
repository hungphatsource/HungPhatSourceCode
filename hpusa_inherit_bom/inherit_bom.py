'''
Created on Apr 14, 2016

@author: Intern ERP Long
'''
from osv import fields, osv


class mrp_bom(osv.osv):
    _inherit = "mrp.bom"
    
    _columns = {
            'product_quality_id': fields.many2one('product.quality.categories', 'Quality Categories'),
                  
                }
    def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            return {'value': {'name': prod.name, 'product_uom': prod.uom_id.id,'product_quality_id':prod.product_quality_id.id  }}
        return {}
mrp_bom()