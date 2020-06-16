# -*- coding: utf-8 -*-
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsApilog(models.Model):
    _name = 'acs.apilog'
    _description = '卡機通訊紀錄'
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
    url = fields.Char(string="網址", required=True)
    request_data = fields.Char(string='原始資料')
    response_data = fields.Char(string='回傳資料')
    
class AcsCardlog(models.Model):
    _name = 'acs.cardlog'
    _description = '刷卡紀錄'
    _rec_name = 'cardlog_id'
    department_code = fields.Char(string='部門代碼')
    department_name = fields.Char(string='部門名稱')
    device_code = fields.Char(string='卡機代碼')
    device_name = fields.Char(string='卡機名稱')
    user_role = fields.Char(string='身份')
    card_id = fields.Char(string='卡片號碼')
    user_name = fields.Char(string='名稱')
    #卡別？
    user_id = fields.Char(string='I D')
    cardlog_time = fields.Datetime(string='刷卡時間')
    cardlog_type = fields.Char(string='刷卡類別')
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
    create_time = fields.Datetime(string='生效時間')
    expire_time = fields.Datetime(string='失效時間')
    accesscode = fields.Char(string='通關密碼')

