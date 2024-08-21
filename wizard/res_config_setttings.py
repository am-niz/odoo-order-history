from odoo import api, fields, models

SALE_ORDER_STATE = [
    ('all', "ALL"),
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    last_no_of_orders = fields.Integer(string="Last No. of Orders")
    last_no_of_days_orders = fields.Integer(string="Last No. of Day's Orders")
    stages = fields.Selection(selection=SALE_ORDER_STATE, string="Stages")
    enable_recorder = fields.Boolean(string="Enable Reorder")

    def set_values(self):
        super(ResConfigSettings, self).set_values()  # to ensure any other settings are save
        param = self.env['ir.config_parameter']
        param.set_param('order_history.last_no_of_orders', str(self.last_no_of_orders))
        param.set_param('order_history.last_no_of_days_orders', str(self.last_no_of_days_orders))
        param.set_param('order_history.stages', self.stages)
        param.set_param('order_history.enable_recorder', 'True' if self.enable_recorder else 'False')
        self.env['sale.order'].search([])._compute_is_enable_reorder()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter']
        res.update(
            last_no_of_orders=int(param.get_param('order_history.last_no_of_orders', default='0')),
            last_no_of_days_orders=int(param.get_param('order_history.last_no_of_days_orders', default='0')),
            stages=param.get_param('order_history.stages'),
            enable_recorder=param.get_param('order_history.enable_recorder', default='False') == 'True'
        )
        return res
