
cd /opt/odoo13
rm -rf odoo-custom-addons.zip
rm -rf odoo-custom-addons
wget https://hq.vegaforce.com.tw/download/odoo/odoo-custom-addons.zip
unzip odoo-custom-addons.zip
ls -lha
mv odoo-custom-addons-mockup/ odoo-custom-addons
chmod 777 -R odoo-custom-addons/
systemctl restart odoo13
systemctl status odoo13


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


    #修改卡片顯示名稱
    # def name_get(self, cr, uid, ids, context=None):
    #     if not len(ids):
    #         return []
    #     res = [(r['id'], r['name'] and '%s [%s]' % (r['name'], r['name2']) or r['name'] ) for r in self.read(cr, uid, ids, ['name', 'name2'], context=context) ]
    #     return res

    # def search_filtered_locker(self):
    #     self.ensure_one()
    #     return {           
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'asc.locker',
    #         'type': 'ir.actions.act_window',
    #         'domain':[('contract_id', '=', '' )],
    #     }
