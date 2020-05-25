# -*- coding: utf-8 -*-
from odoo import fields, models,api

class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '合約設定'

    contract_id = fields.Char(string="合約編號", required=True)
    contract_status = fields.Char(string='狀態') 
    devicegroup = fields.Many2one('acs.devicegroup','門禁群組')
    accesscode =  fields.Char(string="通關密碼")

class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'

    locker_id = fields.Char(string="櫃位編號", required=True)
    locker_type = fields.Char(string="產品種類")
    locker_style = fields.Char(string="類型")
    locker_spec =  fields.Char(string="規格")
    locker_owner = fields.Many2one('hr.department','部門')
    locker_floor = fields.Char(string="樓層")
    locker_vesion = fields.Char(string="期數")
    devicegroup = fields.Many2one('acs.devicegroup','門禁群組')
 
class AcsDevice(models.Model):
    _name = 'acs.device'
    _description = '卡機設定'

    device_id = fields.Char(string="卡機編號", required=True)
    name = fields.Char(string="卡機名稱", required=True)
    device_ip =  fields.Char(string='IP 位址', size=15)
    device_type = fields.Char(string='型號', size=15)
    device_port = fields.Integer( string='卡機Port' )
    node_id = fields.Integer( string='卡機站號' )
    device_location = fields.Char(string='樓層', size=8)
    active = fields.Boolean('連線否', default=True)
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
    device_owner = fields.Many2one('hr.department',string='門市',ondelete='set null')
    devicegroup = fields.Many2one('acs.devicegroup',string='門禁群組',ondelete='set null')

class AcsDeviceGroup(models.Model):
    _name = 'acs.devicegroup'
    _description = '門禁群組設定'
    _rec_name = 'devicegroup_name'

    devicegroup_id = fields.Char(string="群組編號", required=True)
    devicegroup_name = fields.Char(string="群組名稱", required=True)
    device_ids = fields.One2many( 'acs.device','devicegroup',string="所屬卡機")

class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'

    user_role = fields.Many2one( 'res.partner.category' , string="身份")
    card_owner = fields.Many2one( 'res.partner' , string="聯絡人")
    user_id = fields.Char(string='I D',compute='_get_partner_code')
    user_name = fields.Char(string='名稱',compute='_get_partner_name')
    user_phone = fields.Char(string='電話',compute='_get_partner_phone')
    card_id = fields.Char(string='卡片號碼', required=True)
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
    
    contract_ids = fields.One2many('acs.contract', 'id', string="所屬合約")
    
    device_ids = fields.Reference(string='所屬卡機',selection='_select_contract_device')
    
    def _select_contract_device(self):
        
        sql = "select * from acs_device order by name desc;"
        self.env.cr.execute(sql)
        res_all = self.env.cr.fetchall()
        #fetchall() will return an array of dictionaries
        return res_all
        #return self.env['acs.device'].read()
        #devices = []
        #for contract in self.contract_ids:
        #    devices.extend(
        #        self.env['acs.device'].search([('devicegroup', '=', contract.devicegroup)])
        #    )
        #return devices
        #device_ids = fields.Many2many( 'acs.device',  string="所屬卡機" ,
        #relation='contract',column1='devicegroup',column2='devicegroup' )

    def _get_partner_code(self):
        for record in self:
            record.user_id = record.card_owner.vat

    def _get_partner_name(self):
        for record in self:
            record.user_name = record.card_owner.name

    def _get_partner_phone(self):
        for record in self:
            record.user_phone = record.card_owner.phone

class AcsDeviceAccesscode(models.Model):
    _name = 'acs.deviceaccesscode'
    _description = '每日更新通關密碼'

    devicegroup_id = fields.Char(string="通用群組", required=True)
    devicegroup_name = fields.Char(string="群組名稱", required=True)
    accesscode = fields.Char(string="通關密碼", required=True)
    start_time = fields.Datetime(string='有效日期', required=True)
    end_time = fields.Datetime(string='失效日期')
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )

class AcsCardlog(models.Model):
    _name = 'acs.cardlog'
    _description = '刷卡紀錄'

    cardlog_id = fields.Char(string='紀錄編號')
    device_owner = fields.Char(string='門市')
    device_name = fields.Char(string='卡機名稱')
    user_role = fields.Char(string='身份')
    card_id = fields.Char(string='卡片號碼')
    cardlog_type = fields.Char(string='卡別')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    cardlog_time = fields.Datetime(string='刷卡時間')
    cardlog_result = fields.Char(string='刷卡狀態')
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )

class AcsEmployeeCardlog(models.Model):
    _name = 'acs.employeecardlog'
    _description = '員工打卡紀錄'

    employeecardlog_id = fields.Char(string='紀錄編號')
    device_owner = fields.Char(string='門市')
    device_name = fields.Char(string='卡機名稱')
    card_id = fields.Char(string='卡片號碼')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    employeecardlog_type = fields.Char(string='刷卡狀態')
    employeecardlog_time = fields.Datetime(string='刷卡時間')
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )

class AcsCardSettinglog(models.Model):
    _name = 'acs.cardsettinglog'
    _description = '卡片異動紀錄'

    cardsettinglog_id = fields.Char(string='紀錄編號')
    cardsetting_type = fields.Char(string='異動別')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    card_id = fields.Char(string='卡片號碼')
    cardsettinglog_time = fields.Datetime(string='變更時間')
    cardsettinglog_user = fields.Char(string='變更者')    
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )

class AcsAccessCodelog(models.Model):
    _name = 'acs.accesscodelog'
    _description = '個人通關密碼設定紀錄'

    accesscodelog_id = fields.Char(string='紀錄編號')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    devicegroup_name = fields.Char(string='門禁群組')
    create_time = fields.Datetime(string='變更時間')
    expire_time = fields.Datetime(string='有效時間')
    accesscode = fields.Char(string='通關密碼')    
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
