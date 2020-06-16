# -*- coding: utf-8 -*-
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class Department(models.Model):
    _inherit = 'hr.department'
    code = fields.Char(string="部門代碼")

class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'
    _rec_name = 'code'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    status = fields.Selection([ ('閒置', '閒置'),('租用中', '租用中'),('自用', '自用'),('停用', '停用'),],'櫃位狀態', default='閒置', required=True)
    code = fields.Char(string="櫃號", required=True)
    category = fields.Selection([ ('倉庫', '倉庫'),('工作空間', '工作空間'),('經典車庫', '經典車庫'),('公司登記', '公司登記'),],string="租賃類別", default='倉庫', required=True)
    style = fields.Char(string="類型", required=True)
    spec =  fields.Char(string="規格", required=True)
    floor = fields.Char(string="樓層", required=True)
    vesion = fields.Char(string="期數", required=True)

    devicegroup_id = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')
    
    department_id = fields.Many2one('hr.department','所屬部門',ondelete='set null')
    
    contract_id = fields.Many2one('acs.contract','所屬合約',ondelete='set null')

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsLocker, self).unlink()

class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '????'
    _rec_name = 'code'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    partner_id = fields.Many2one('res.partner','客戶', required=True)

    code = fields.Char(string="合約編號", required=True)

    locker_id = fields.Many2one('acs.locker','櫃位', required=True)

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsContract, self).unlink()
