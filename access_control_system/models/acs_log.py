# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)
    
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
    user_id = fields.Char(string='I D')
    cardlog_time = fields.Datetime(string='刷卡時間')
    cardlog_type = fields.Char(string='刷卡類別')
    cardlog_result = fields.Char(string='刷卡狀態')
    cardlog_source = fields.Char(string='卡別') #驗證來源：卡片 密碼

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

    @api.model
    def create(self, vals):
        #_logger.warning('create self: %s' % (self) )
        #_logger.warning('create vals: %s' % (vals) )
        result = super(AcsCardSettinglog, self).create(vals)
        if 'data_new' in vals:
            new_vals = eval( vals["data_new"] ) #, type( eval(vals["data_new"]) )
            #_logger.warning('AcsCardSettinglog create vals: %s' % (vals) )
            #_logger.warning('data_new vals: %s' % (new_vals) )

            #json.loads(vals["data_new"])
            if 'pin' in new_vals:
                card = self.env['acs.card'].sudo().search([ ('uid','=',vals['card_id']) , ('status','=','啟用') ] )
                devicegroup_names = ''
                if 'devicegroup_ids' in card:
                    for dg in card.devicegroup_ids:
                        devicegroup_names += dg.code + ','

                codelog = {
                    'accesscodelog_id': vals['cardsettinglog_id'],
                    'user_role': vals['user_role'],
                    'user_id': vals['user_id'],
                    'user_name': vals['user_name'],
                    'devicegroup_name' : devicegroup_names,
                    'create_time': datetime.datetime.now(),
                    'expire_time': datetime.datetime.now() + timedelta(hours=3),
                    'accesscode': new_vals['pin'],
                }
                self.env['acs.accesscodelog'].sudo().create([codelog])
        return result

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

