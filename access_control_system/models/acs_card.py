# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

_logger = logging.getLogger(__name__)

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

    #員工廠商授權進入的門禁群組 改Many2many
    devicegroup_ids = fields.Many2many(
        string='授權門禁群組',
        comodel_name='acs.devicegroup',
        relation='acs_devicegroup_acs_card_rel',
        column1='devicegroup_id',
        column2='card_id',
    )
    
    #客戶租用櫃位清單
    locker_ids = fields.One2many('acs.locker', 'card', string="合約清單",readonly=True)

#for compute fields
    def _get_owner_role(self):
        for record in self:
            record_role = ''
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

#card ORM methods
    def create(self, vals):
        _log2table(self ,'新增' ,vals)
        result = super(AcsCard, self).create(vals)
        return result
    
    def write(self,vals):
        _log2table(self ,'修改' ,vals)
        result = super(AcsCard, self).write(vals)
        return result

    def unlink(self):
        _log2table(self ,'刪除' ,{})
        result = super(AcsCard, self).unlink()
        return result


def _log2table(self ,cardsetting_type ,vals):

    _logger.warning( cardsetting_type )
    _logger.warning( self )
    _logger.warning( 'vals:' + json.dumps(vals) )

    cards2delete =[]
    cards2add=[]
    cards2update = []
    
    ldata = {
        'cardsettinglog_id': '',
        'cardsetting_type':cardsetting_type,
        'user_role': '',
        'user_id': '',
        'user_name': '',
        'card_id' : '',
        'data_origin': '' ,
        'data_new': json.dumps(vals),
        'cardsettinglog_time': datetime.datetime.now(),
        'cardsettinglog_user': self.env.user.name
    }
    recordcount = 0
    #for update/delete
    for record in self:
        recordcount+=1
        _logger.warning( 'update/delete:' + str(recordcount) )
        #keep old vals in data_origin
        vals_old ={
            'user_role': record.user_role,
            'user_id': record.user_id, 
            'user_name': record.user_name,
            'card_id' : record.card_id,
            'card_pin' : record.card_pin,
        }
        #use old vals for display
        ldata['user_role'] =record.user_role
        ldata['user_id'] =record.user_id
        ldata['user_name'] = record.user_name
        ldata['card_id'] = record.card_id
        ldata['data_origin'] =json.dumps(vals_old)

        #TODO: build 1 request for api/devices-async
        # A: build card lists from CRUD operations following up
        # C: log into logtable
        # B: build devices-card-action list from card lists
        #    card --> locker relate group + authorized groups --> relate devices
        # D: build request by devices-card-action list in delete,add,update order
        # E: send request
        
        if vals == {}:
            _logger.warning( 'THIS IS DELETE!!!!!' )
            #A1 build delete list
            cards2delete.append({
                    "event": "delete",
                    'uid' : record.card_id,
                    'id': record.id,
                })
        else:
            _logger.warning( 'THIS IS UPDATE!!!!!' )
            if 'card_id' in vals:
                #use new overwrite display cols when changing card_id
                _logger.warning( 'card_id change!' )
                ldata['card_id'] = vals['card_id']
                ldata['cardsetting_type'] = '變更卡號'
                #A2 build delete & addnew list
                cards2delete.append({
                    "event": "delete",
                    'uid' : record.card_id,
                    'id': record.id,
                })
                cards2add.append({ 
                    "event": "add",
                    "expire_start": "2030-05-01",
                    "expire_end": "2030-05-31",
                    'uid' : vals['card_id'],
                    'display' :  record.user_name,
                    'pin': record.card_pin,
                    'id': record.id,
                })
            else:
                _logger.warning( 'card_id no change!' )
            
            if 'card_pin' in vals:
                #TODO A3 build update list
                _logger.warning( 'card_pin change!' )
                ldata['cardsetting_type'] = '變更密碼'
                cards2update.append({ 
                    "event": "update",
                    "expire_start": "2030-05-01",
                    "expire_end": "2030-05-31",
                    'uid' : record.card_id,
                    'display' :  record.user_name,
                    'pin': vals['card_pin'],
                    'id': record.id,
                })
            else:
                _logger.warning( 'card_pin no change!' )
        #C1: log into logtable
        ldata['cardsettinglog_id'] = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        self.env['acs.cardsettinglog'].sudo().create([ldata])
        _logger.warning( ldata )
    #for addnew--> not update or delete
    if recordcount == 0:
        _logger.warning( 'THIS IS CREATE!!!!!' )
        for val in vals:
            recordcount+=1
            if 'card_id' in val:
                _logger.warning( 'new card_id!' + str(recordcount) )
                ldata['card_id'] = val['card_id']
                #C2: log into logtable
                ldata['cardsettinglog_id'] = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
                self.env['acs.cardsettinglog'].sudo().create([ldata])
                _logger.warning( ldata )
            else:                
                _logger.warning( 'WARNIG!!! MISSING card_id!' + str(recordcount))
        #no need to send request here
        return
    # D: build request by devices-card-action list in delete,add,update order
    call_devices_async(self,cards2delete)
    call_devices_async(self,cards2add)
    call_devices_async(self,cards2update)

def call_devices_async(self,cards):
    logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
    payload={ "logid": logid, "device": [] }

    for card in cards:
        
        searchresult = self.env['acs.card'].sudo().search([['id','=',card['id'] ] ])
        if searchresult :
            for c in searchresult:
        # B1 search authorized groups
                for dg in c.devicegroup_ids:
                    for d in dg.device_ids:
                        payload["device"].append({
                            "device_id": d.device_id,
                            "ip": d.device_ip,
                            "port": d.device_port,
                            "node": d.node_id,
                            "card": [ card ]
                        })
                for lk in c.locker_ids:
        # B2 search locker related group
                    if lk.devicegroup:
                        for d in lk.devicegroup.device_ids:
                            payload["device"].append({
                                "device_id": d.device_id,
                                "ip": d.device_ip,
                                "port": d.device_port,
                                "node": d.node_id,
                                "card": [ card ]
                            })
    if len(payload["device"]) > 0:
        
        _logger.warning('sending request: %s' % (json.dumps(payload) ) )
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )
        # E: begin send request to /api/devices-async
        r = requests.post(deviceserver+'/api/devices-async',data=json.dumps(payload))
        _logger.warning('%s, %s, %s' % (logid,r.status_code, r._content))
        message = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
            'title': r.status_code,
            'message': r._content,
            'sticky': True,
            }
        }
        if r.status_code != requests.codes.ok:
            message['params']['message'] = 'something goes wrong'
        return message

