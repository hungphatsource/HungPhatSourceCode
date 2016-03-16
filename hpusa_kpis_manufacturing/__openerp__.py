{
    "name": "KPIS Manufacturing",
    "version": "1.2",
    "author": "thanhdongcntt",
    "category": "HPUSA module",
    "website": "",
    "description": """
    Manufacturing Module
    """,
    'depends': ["base","mrp","product",'hpusa_manufacturing_planning','hpusa_groups','hpusa_chart'],
    'init_xml': [],
    'update_xml': [
                   "hp_daily_report_view.xml",
                   "product_view.xml",
                   "hp_configuration_view.xml",
                   "wizard/wizard_hp_report_kpis_view.xml",
                   "wizard/wizard_hp_report_kpis_chart_view.xml",
                   "wizard/hp_kpis_view_chart_view.xml",
                   "hpusa_kpis_manufacturing_report.xml",
                   "hp_target_view.xml"
                   ],
    'installable': True,
    'active': False,
}