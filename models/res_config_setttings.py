from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    last_no_of_orders = fields.Integer(string="Last No. of Orders")
    last_no_of_days_orders = fields.Integer(string="Last No. of Day's Orders")
    stages = fields.Selection([
        ('sample1', 'Sample1'),
        ('sample2', 'Sample2'),
        ('all', 'All')
    ], string="Stages")
    enable_recorder = fields.Boolean(string="Enable Reorder")

    def set_values(self):
        super(ResConfigSettings, self).set_values()  # to ensure any other settings are save
        param = self.env['ir.config_parameter']
        param.set_param('order_history.last_no_of_orders', str(self.last_no_of_orders))
        param.set_param('order_history.last_no_of_days_orders', str(self.last_no_of_days_orders))
        param.set_param('order_history.stages', self.stages)
        param.set_param('order_history.enable_recorder', str(self.enable_recorder))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter']
        res.update(
            last_no_of_orders=int(param.get_param('order_history.last_no_of_orders', default='0')),
            last_no_of_days_orders=int(param.get_param('order_history.last_no_of_days_orders', default='0')),
            stages=param.get_param('order_history.stages'),
            enable_recorder=param.get_param('order_history.enable_recorder', default='False')
        )
        return res