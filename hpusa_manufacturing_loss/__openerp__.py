{
    "name": "Manufacturing Loss",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "HPUSA module",
    "website": "",
    "description": """
    Manufacturing Loss Module
    """,
    'depends': ["mrp","sale","hr","mrp_operations","hpusa_material_request","mrp_repair","gs_hpusa_order"],
    'init_xml': [],
    'update_xml': [
                   "wizard/hpusa_manufacturing_loss_view.xml",
                   "views/hpusa_product_view.xml",
                   "views/manufacturing_loss_report_view.xml",
                   ],
    'installable': True,
    'active': False,
}