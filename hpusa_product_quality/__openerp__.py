{
    "name": "Product Quality Categories",
    "version": "1.1",
    "author": "Thanh Thuan Lieu",
    "category": "HPUSA module",
    "website": "",
    "description": """
    Create Product Quality Categories
    """,
    'depends': ["mrp","sale","hr","product","gs_hpusa_order"],
    'init_xml': [],
    'update_xml': [
                   "view/hpusa_product_view.xml",
                   "view/hpusa_quality_category.xml",
                   ],
    'installable': True,
    'active': False,
}