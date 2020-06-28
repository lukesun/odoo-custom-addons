# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

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
    
    cardsettinglog_id = fields.Char(string='紀錄編號', required=True)
    cardsetting_type = fields.Char(string='異動別')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    card_id = fields.Char(string='卡片號碼', required=True)
    data_origin = fields.Char(string='原始')
    data_new = fields.Char(string='變更')
    cardsettinglog_time = fields.Datetime(string='變更時間', required=True)
    cardsettinglog_user = fields.Char(string='變更者', required=True)
    status = fields.Char(string='狀態')

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

    def scan(self):
        #TODO: build 1 request for api/devices-async
        # A: build card lists from CRUD operations following up
        # C: log into logtable
        # B: build devices-card-action list from card lists
        #    card --> locker relate group + authorized groups --> relate devices
        # D: build request by devices-card-action list in delete,add,update order
        # E: send request

        _logger.warning('scan start at: %s' % (datetime.datetime.now()) )
        logs = self.env['acs.cardsettinglog'].sudo().search([ 
            ('cardsetting_type','in',['變更卡號','變更密碼','變更群組','變更合約','作廢']) , 
            ('status','!=','ok') 
        ] )
        cards2delete =[]
        cards2add=[]
        cards2update = []
        for log in logs:
            
            cards2delete.append({
                    "event": "delete",
                    'uid' : log.card_id,
                })
            
            cards2add.append({ 
                    "event": "add",
                    "expire_start": "2020-05-01",
                    "expire_end": "2030-05-31",
                    'uid' : log.card_id,
                    'display' : log.user_name,
                })
            
            cards2update.append({ 
                "event": "update",
                "expire_start": "2020-05-01",
                "expire_end": "2030-05-31",
                'uid' : log.card_id,
                'display' :  log.user_name,
                #'pin': vals['pin'],
            })            

        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        payload={ "logid": logid, "device": [] }

        # for d in self.device_ids:
        #     payload["device"].append({
        #         "device_id": d.device_id,
        #         "ip": d.device_ip,
        #         "port": d.device_port,
        #         "node": d.node_id,
        #         "card": cards
        #     })

        # # call api to update locker's devicegroup's devices
        _logger.warning('sending request: %s' % (json.dumps(payload) ) )
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )
        # r = requests.post(deviceserver+'/api/devices-async',data=json.dumps(payload))
        # _logger.warning('%s, %s, %s' % (logid,r.status_code, r._content))
        # if r.status_code != requests.codes.ok:
        #     message['params']['message'] = 'something goes wrong'
        _logger.warning('scan end at: %s' % (datetime.datetime.now()) )

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

