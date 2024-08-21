from odoo import models, fields, api
from datetime import timedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_history_ids = fields.One2many(
        "order.history",
        "sale_order_id",
        string="Order History",
        compute="_compute_order_history_ids",
        store=True,
        depends=['partner_id']  # order history changes with respect to partner_id
    )

    limited_order_history_ids = fields.One2many(
        "order.history",
        "sale_order_id",
        compute="_compute_limited_order_history",
        string="Limited Order History"
    )
    is_enable_reorder = fields.Boolean(
        string="Enable Reorder",
        compute="_compute_is_enable_reorder",
        store=True
    )

    @api.depends('partner_id')
    def _compute_is_enable_reorder(self):
        param = self.env['ir.config_parameter'].sudo().get_param('order_history.enable_recorder', 'False')
        enabled = param.lower() == 'true'
        for record in self:
            record.is_enable_reorder = enabled

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
                        """
                        0: The first 0 indicates that you want to create a new record.
                        0: The second 0 is the ID of the record. Since you are creating a new record, 
                        you don't have an ID yet, so it's set to 0.
                        """
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
        last_no_of_days_limit = int(self.env['ir.config_parameter'].get_param('order_history.last_no_of_days_orders', '3'))
        stages = self.env['ir.config_parameter'].get_param('order_history.stages')
        last_orders_limit = int(self.env['ir.config_parameter'].get_param('order_history.last_no_of_orders', '10'))
        recent_dates = self.get_recent_dates(last_no_of_days_limit)

        for record in self:
            new_limited_order_history = []
            for line in record.order_history_ids:
                if line.order_date.date() in recent_dates and (stages == 'all' or line.order_status == stages):
                    new_limited_order_history.append(line)
            record.limited_order_history_ids = [(6, 0, [line.id for line in new_limited_order_history[:last_orders_limit]])]

            # in [(6, 0, [ids])] tuple 6 for replacing
            """
            6: The 6 in this tuple indicates a special operation for Many2many or One2many fields. 
                It means "replace the entire set of linked records with the records specified by the IDs in the list."
            0: The 0 is not used in this context, but it must be included in the tuple structure.
            [ids]: This is a list of IDs that you want to set for the field. 
                It replaces any existing linked records with these new ones.
            """

    def get_recent_dates(self, n):
        today = fields.Date.today()
        recent_dates = [(today - timedelta(days=i)) for i in range(n)]
        return recent_dates

    def button_all_history_add_to_order(self):
        self.ensure_one()
        for history in self.limited_order_history_ids:
            values = {
                'order_id': self.id,
                'product_id': self.env['product.product'].search([('name', '=', history.order_product)], limit=1).id,
                'name': history.order_product,
                'product_uom_qty': history.order_quantity,
                'price_unit': history.order_price,
                'discount': history.order_discount,
            }
            self.env['sale.order.line'].create(values)
        return True
