# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'
    _rec_name = 'locker_id'
    locker_id = fields.Char(string="櫃位編號", required=True)
    locker_type = fields.Char(string="產品種類")
    locker_style = fields.Char(string="類型")
    locker_spec =  fields.Char(string="規格")
    locker_floor = fields.Char(string="樓層")
    locker_vesion = fields.Char(string="期數")
    confirmDelte = fields.Boolean(string='確認刪除', default=False)
    
    locker_owner = fields.Many2one('hr.department','所屬部門',ondelete='set null')

    devicegroup = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsLocker, self).unlink()
        else:
            self.write({'devicegroup': False})
            return True

#改為卡片vs合約的紀錄表 (one2many)
class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '合約設定'
    _rec_name = 'contract_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)
    card = fields.Many2one('acs.card',string='所屬卡片',ondelete='set null')

    _sql_constraints = [
        ('unique_contract_id', 'unique(contract_id)', '合約編號不能重複！')
        ]

    contract_id = fields.Char(string="合約編號", required=True, readonly=True ) 
    devicegroup = fields.Many2one('acs.devicegroup','所屬門禁群組',ondelete='set null' , readonly=True)

    locker = fields.Many2one('acs.locker',string='所屬櫃位',ondelete='set null')
    contract_status = fields.Boolean(string='狀態', default=True)

#依選擇的櫃位產生合約編號
    @api.onchange('locker')
    def _onchange_locker(self):
        if self.devicegroup:
            self.devicegroup = self.locker.devicegroup
            c_id = self.locker.locker_id + ( datetime.datetime.now() + timedelta(hours=8) ).strftime('%Y%m%d')
            _logger.warning('contract_id:%s' % (c_id ) )
            self.contract_id=c_id
        else:
            self.contract_id=''

    def unlink(self):
        self.write({'locker': False,'card': False ,'devicegroup':False})
        return True
