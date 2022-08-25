# -*- coding: utf-8 -*-


{
    'name': 'BAR EXTRA',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 6,
    'summary': 'Módulo para el BAR',
    'description': """

""",
    'depends': ['base','point_of_sale','product'],
    'data': [
        'wizards/reporte_ventas_diario_wizard_view.xml',
        'views/product_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
