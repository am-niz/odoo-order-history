from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_line_history_ids = fields.One2many("order.history", 'line_id', 'Order History Lines')
