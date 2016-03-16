from osv import fields, osv

class product_quality_categories(osv.osv):
    _name = "product.quality.categories"
    _description= "Product Quality Categories"
    
    
    _columns = {
            'name': fields.char('Name', required=True),
            'description': fields.text('Description'), 
    }
    
product_quality_categories()