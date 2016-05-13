from osv import fields, osv


class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
            'product_quality_id': fields.many2one('product.quality.categories', 'Quality Categories'),
                  
                }
    
product_product()