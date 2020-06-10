# -*- coding: utf-8 -*-
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsServicelog(models.Model):
    _name = 'acs.servicelog'
    _description = '卡機通訊紀錄'
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
    request_data = fields.Char(string='原始資料')

class AcsCardlog(models.Model):
    _name = 'acs.cardlog'
    _description = '刷卡紀錄'
    _rec_name = 'cardlog_id'
    device_owner = fields.Char(string='門市')
    device_name = fields.Char(string='卡機名稱')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    card_id = fields.Char(string='卡片號碼')
    cardlog_time = fields.Datetime(string='刷卡時間')
    cardlog_type = fields.Char(string='卡別')
    cardlog_result = fields.Char(string='刷卡狀態')
    cardlog_id = fields.Char(string='紀錄編號')
    cardlog_data = fields.Char(string='卡機資料')

class AcsCardSettinglog(models.Model):
    _name = 'acs.cardsettinglog'
    _description = '卡片異動紀錄'
    _rec_name = 'cardsettinglog_id'
    
    cardsettinglog_id = fields.Char(string='紀錄編號')
    cardsetting_type = fields.Char(string='異動別')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    card_id = fields.Char(string='卡片號碼')
    data_origin = fields.Char(string='原始')
    data_new = fields.Char(string='變更')
    cardsettinglog_time = fields.Datetime(string='變更時間')
    cardsettinglog_user = fields.Char(string='變更者')    

class AcsAccessCodelog(models.Model):
    _name = 'acs.accesscodelog'
    _description = '個人通關密碼設定紀錄'
    _rec_name = 'accesscodelog_id'

    accesscodelog_id = fields.Char(string='紀錄編號')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    devicegroup_name = fields.Char(string='門禁群組')
    create_time = fields.Datetime(string='變更時間')
    expire_time = fields.Datetime(string='有效時間')
    accesscode = fields.Char(string='通關密碼')
