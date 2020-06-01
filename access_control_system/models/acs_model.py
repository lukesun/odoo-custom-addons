# -*- coding: utf-8 -*-
import datetime
import requests
import json
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

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
            deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.config.settings.deviceserver')
        )
        return res

    def set_values(self):
        super(AcsConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('acs.config.settings.deviceserver', self.use_security_lead)

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

class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'

    locker_id = fields.Char(string="櫃位編號", required=True)
    locker_type = fields.Char(string="產品種類")
    locker_style = fields.Char(string="類型")
    locker_spec =  fields.Char(string="規格")
    locker_floor = fields.Char(string="樓層")
    locker_vesion = fields.Char(string="期數")

    locker_owner = fields.Many2one('hr.department','所屬部門',ondelete='set null')

    devicegroup = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')

    def unlink(self):
        self.write({'devicegroup': False})
        return True

