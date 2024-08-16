# -*- coding: utf-8 -*-
{
    'name': "Order History",

    'summary': "A Page of Order Histories",

    'description': """
It used to display a page that contains the customer's previous order.
    """,

    'author': "NIZAMUDHEEN MJ",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
    ],
    "application": True,
    "sequence": -93,
    'license': 'AGPL-3',
}

