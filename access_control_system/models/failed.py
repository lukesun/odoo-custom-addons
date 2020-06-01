class AcsConfigSettings(models.TransientModel):
    _name = 'acs.config.settings'
    _inherit = 'res.config.settings'
    
    deviceserver = fields.Char(string='卡機伺服器網址')

    def _onchange_deviceserver(self):
        if not self.deviceserver:
            self.deviceserver = "http://odooerp.morespace.com.tw:9090"

    def get_values(self):
        res = super(AcsConfigSettings, self).get_values()
        res.update(
            deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        )
        return res

    def set_values(self):
        super(AcsConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('acs.deviceserver', self.deviceserver)

#class AcsCardOwner(models.Model):
#    _name = 'acs.cardowner'
#    _description = '卡片所有人'
#    _inherit = 'res.partner'

#    @api.model
#    def name_search(self, name='', args=None, operator='ilike', limit=100):
#        if self._context.get('search_by_vat', False):
#            if name:
#                args = args if args else []
#                args.extend(['|', ['name', 'ilike', name], ['vat', 'ilike', name]])
#                name = ''
#        return super(AcsCardOwner, self).name_search(name=name, args=args, operator=operator, limit=limit)
