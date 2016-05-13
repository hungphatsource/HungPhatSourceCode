from openerp.osv import osv, fields
import time


class material_request(osv.Model):
    _name = "material.request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name': fields.char("Name", size=128, required=True),
        'requester': fields.many2one('hr.employee', 'Requester'),
        'receipter': fields.many2one('hr.employee', 'Receipter'),
        'date_request': fields.datetime("Date Request"),
        'date_transfer': fields.datetime("Date Transfer", readonly=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting Available'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the material request.", select=True),

        'material_request_line_ids': fields.one2many('material.request.line', 'material_request_id')
    }

    _defaults = {
        'state': 'draft',
        'date_request': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }

    def action_button_send_to_manager(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids[0], {'state': 'waiting'})
        return True

    def action_button_transfer(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids[0], {'state': 'done', 'date_transfer': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_button_set_to_draft(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids[0], {'state': 'draft', 'date_transfer': None})
        return True


class material_request_line(osv.Model):
    _name = "material.request.line"
    _columns = {
        'material_request_id': fields.many2one("material.request", size=128, required=True),
        'product_id': fields.many2one("product.product", "Product", size=128, required=True),
        'quantity': fields.integer('Quantity'),
        'weight': fields.float('Weight'),
        'unit': fields.related('product_id', 'product_tmpl_id', 'uom_id', type="many2one", relation="product.uom", string="Unit", readonly=True),
        }
