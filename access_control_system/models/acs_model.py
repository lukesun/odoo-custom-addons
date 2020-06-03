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
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    locker_id = fields.Char(string="櫃位編號", required=True)
    locker_type = fields.Char(string="產品種類")
    locker_style = fields.Char(string="類型")
    locker_spec =  fields.Char(string="規格")
    locker_floor = fields.Char(string="樓層")
    locker_vesion = fields.Char(string="期數")
    
    locker_owner = fields.Many2one('hr.department','所屬部門',ondelete='set null')

    devicegroup = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')
    
    contract = fields.Many2one('acs.contract','所屬合約',ondelete='set null')

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsLocker, self).unlink()
        else:
            self.write({'devicegroup': False})
            return True

class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '合約設定'
    _rec_name = 'contract_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)
    #改為卡片vs合約的紀錄表 (one2many)
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
        if self.confirmUnlink:
            return super(AcsContract, self).unlink()
        else:
            self.write({'locker': False,'card': False ,'devicegroup':False})
            return True

class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'
    _rec_name = 'card_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    card_owner = fields.Many2one( 'res.partner' , string="聯絡人")
    card_id = fields.Char(string='卡片號碼', required=True)
    card_pin = fields.Char(string='卡片密碼')

    user_id = fields.Char(string='I D',compute='_get_owner_id')
    user_name = fields.Char(string='名稱',compute='_get_owner_name')
    user_phone = fields.Char(string='電話',compute='_get_owner_phone')
    user_role = fields.Char(string='身份',compute='_get_owner_role')

    #員工廠商授權進入的門禁群組
    #devicegroup_ids = fields.One2many('acs.devicegroup', 'card', string="授權門禁群組")

    #客戶租用櫃位清單
    contract_ids = fields.One2many('acs.contract', 'card', string="合約清單")

    @api.model
    def create(self, vals):
        _logger.warning('acs.card create:%s' % ( vals ) )
        #TODO: call api to add card setting
        result = super(AcsCard, self).create(vals)
        return result

    def write(self,vals):
        _logger.warning('acs.card write:%s' % ( vals ) )
        #TODO: call api to update card setting
        result = super(AcsCard, self).write(vals)
        return result

    def unlink(self):
        _logger.warning('acs.card unlink:%s' % ( self.card_id ) )
        #TODO: call api to delete card setting
        result = super(AcsCard, self).unlink()
        return result
    
    def _get_owner_role(self):
        #TODO 
        for record in self:
            record_role = '未定'
            record.user_role = record_role

    def _get_owner_id(self):
        for record in self:
            record.user_id = record.card_owner.vat

    def _get_owner_name(self):
        for record in self:
            record.user_name = record.card_owner.name

    def _get_owner_phone(self):
        for record in self:
            record.user_phone = record.card_owner.phone
