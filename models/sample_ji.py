from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_history_ids = fields.One2many(
        comodel_name='order.history',
        inverse_name='order_id',
        string='Order History'
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):

        if self.partner_id:
            self.order_history_ids = [(5, 0, 0)]

            config_param = self.env['ir.config_parameter'].sudo()
            last_no_of_orders = int(config_param.get_param('sale.last_no_of_orders', 0))
            order_stages = config_param.get_param('sale.order_stages', 'all')

            domain = [('partner_id', '=', self.partner_id.id)]
            if order_stages != 'all':
                domain.append(('state', '=', order_stages))

            sale_orders = self.env['sale.order'].search(domain, order='date_order desc', limit=last_no_of_orders)

            histories = []
            for order in sale_orders:
                for line in order.order_line:
                    histories.append((0, 0, {
                        'order_id': order.id,
                        'order_line_id': line.id,
                        'order_history_selected': False,
                    }))
            self.order_history_ids = histories

    def action_reorder(self):
        if not self.env['ir.config_parameter'].sudo().get_param('sale.enable_reorder', False):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reorder Disabled',
                'view_mode': 'form',
                'res_model': 'res.config.settings',
                'target': 'new',
            }

        new_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'state': 'draft',
        })

        order_lines = []
        for history in self.order_history_ids.filtered('order_history_selected'):
            order_lines.append((0, 0, {
                'product_id': history.product_id.id,
                'product_uom_qty': history.product_uom_qty,
                'price_unit': history.price_unit,
                'discount': history.discount,
            }))
        new_order.write({'order_line': order_lines})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': new_order.id,
            'target': 'current',
        }