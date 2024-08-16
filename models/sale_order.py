from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import date_utils


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_history_ids = fields.One2many(
        "order.history",
        "sale_order_id",
        string="Order History",
        compute="_compute_order_history_ids",
        store=True,
        depends=['partner_id']
    )

    limited_order_history_ids = fields.One2many(
        "order.history",
        "sale_order_id",
        compute="_compute_limited_order_history",
        string="Limited Order History"
    )

    @api.model
    def _compute_order_history_ids(self):
        # print("Computing order history ids...")
        for record in self:
            if record.partner_id:
                domain = [
                    ('partner_id', '=', record.partner_id.id)
                ]
                if record.id:
                    domain.append(('id', '!=', record.id))
                orders = self.env['sale.order'].search(domain)
                histories = []
                for order in orders:
                    for line in order.order_line:
                        histories.append((0, 0, {
                            'order_number': order.name,
                            'order_date': order.date_order,
                            'order_product': line.product_id.name,
                            'order_price': line.price_unit,
                            'order_quantity': line.product_uom_qty,
                            'order_discount': line.discount,
                            'order_sub_total': line.price_subtotal,
                            'order_status': order.state,
                            'sale_order_id': order.id,
                        }))
                record.order_history_ids = histories

    @api.depends("order_history_ids")
    def _compute_limited_order_history(self):
        last_orders_limit = int(self.env['ir.config_parameter'].get_param('order_history.last_no_of_days_orders', '3'))
        recent_dates = self.get_recent_dates(last_orders_limit)
        last_no_of_days_limit = int(self.env['ir.config_parameter'].get_param('order_history.last_no_of_orders', '10'))
        for record in self:
            new_limited_order_history_ids = []
            for line in record.order_history_ids:
                if line.order_date.date() in recent_dates:
                    new_limited_order_history_ids.append(line)
            record.limited_order_history_ids = [(6, 0, [line.id for line in new_limited_order_history_ids[:last_no_of_days_limit]])]
            # in tuple 6 for replacing
    def get_recent_dates(self, n):
        today = fields.Date.today()
        recent_dates = [(today - timedelta(days=i)) for i in range(n)]
        return recent_dates
