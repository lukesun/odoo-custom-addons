# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

_logger = logging.getLogger(__name__)

def write_card_log(self ,vals):

    _logger.warning( self )
    _logger.warning( 'vals:' + json.dumps(vals) )

    cards2delete =[]
    cards2add=[]
    cards2update = []
    
    ldata = {
        'cardsettinglog_id': '',
        'cardsetting_type':'',
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
            'user_id': record.user_code, 
            'user_name': record.user_name,
            'card_id' : record.uid,
            'card_pin' : record.pin,
        }
        #use old vals for display
        ldata['user_role'] =record.user_role
        ldata['user_id'] =record.user_code
        ldata['user_name'] = record.user_name
        ldata['card_id'] = record.uid
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
            ldata['cardsetting_type'] = '刪除'
            #A1 build delete list
            cards2delete.append({
                    "event": "delete",
                    'uid' : record.uid,
                    'id': record.id,
                })
        else:
            _logger.warning( 'THIS IS UPDATE!!!!!' )
            ldata['cardsetting_type'] = '修改'
            if 'card_id' in vals:
                #use new overwrite display cols when changing card_id
                _logger.warning( 'card_id change!' )
                ldata['card_id'] = vals['card_id']
                ldata['cardsetting_type'] = '變更卡號'
                #A2 build delete & addnew list
                cards2delete.append({
                    "event": "delete",
                    'uid' : record.uid,
                    'id': record.id,
                })
                cards2add.append({ 
                    "event": "add",
                    "expire_start": "2020-05-01",
                    "expire_end": "2030-05-31",
                    'uid' : vals['uid'],
                    'display' :  record.user_name,
                    'pin': record.pin,
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
                    "expire_start": "2020-05-01",
                    "expire_end": "2030-05-31",
                    'uid' : record.uid,
                    'display' :  record.user_name,
                    'pin': vals['pin'],
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
        ldata['cardsetting_type'] = '新增'
        if 'card_id' in vals:
        #use new card_id as logdata
            _logger.warning( 'create with card_id:' + vals['card_id'])
            ldata['card_id'] = vals['card_id']
        #C2: log into logtable
        ldata['cardsettinglog_id'] = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        self.env['acs.cardsettinglog'].sudo().create([ldata])
        _logger.warning( ldata )
        #no need to send request here
        return
    #D: build request by devices-card-action list in delete,add,update order
    _logger.warning('call_devices_async, delete: %s' % (json.dumps(cards2delete) ) )
    #call_devices_async(self,cards2delete)
    _logger.warning('call_devices_async, add: %s' % (json.dumps(cards2add) ) )
    #call_devices_async(self,cards2add)
    _logger.warning('call_devices_async, update: %s' % (json.dumps(cards2update) ) )
    #call_devices_async(self,cards2update)

""" def call_devices_async(self,cards):    
    logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
    payload={ "logid": logid, "device": [] }

    for card in cards:
        
        searchresult = self.env['acs.card'].sudo().search([['id','=',card['id'] ] ])
        if searchresult :
            # B search authorized groups
            for c in searchresult:
                for dg in c.devicegroup_ids:
                    for d in dg.device_ids:
                        payload["device"].append({
                            "device_id": d.code,
                            "ip": d.ip,
                            "port": d.port,
                            "node": d.node,
                            "card": [ card ]
                        })
    if len(payload["device"]) > 0:
        
        _logger.warning('sending request: %s' % (json.dumps(payload) ) )
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )
        # E: begin send request to /api/devices-async
        r = requests.post(deviceserver+'/api/devices-async',data=json.dumps(payload))
        _logger.warning('%s, %s, %s' % (logid,r.status_code, r._content))
        #if r.status_code != requests.codes.ok:
        #    'something goes wrong'
 """
#更新卡機設定
def call_devices_async(self,vals):
    _logger.warning( 'vals[card_ids]: %s' %(vals['card_ids']) )
    _logger.warning( 'vals[card_ids][0][2]: %s' %(vals['card_ids'][0][2]) )
    _logger.warning( 'self.card_ids: %s' %(self.card_ids) )
    cards = []
    for c2d in self.card_ids:
        if c2d.id not in vals['card_ids'][0][2]:
            _logger.warning( 'card to delete: %s' %(c2d.card_id) )
            cards.append({
                "event": "delete",
                'uid' : c2d.card_id,
            })
            log_del = {
                'cardsettinglog_id': (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f'),
                'cardsetting_type':'門禁群組變更',
                'user_role': '客戶',
                'user_id': c2d.user_id,
                'user_name': c2d.user_name,
                'card_id' : c2d.card_id,
                'data_origin': '退出群組:%s' %(self.devicegroup_name) ,
                'data_new': '',
                'cardsettinglog_time': datetime.datetime.now(),
                'cardsettinglog_user': self.env.user.name
            }
            self.env['acs.cardsettinglog'].sudo().create([log_del])
    addCheck = True
    for cid2add in vals['card_ids'][0][2]:
        addCheck = True
        for oldcard in  self.card_ids:
            if oldcard.id == cid2add:
                addCheck = False
        if addCheck == True:
            _logger.warning( 'card to add by id: %s' %(cid2add) )
            card2add = self.env['acs.card'].sudo().search([['id','=',cid2add ] ])
            cards.append({
                "event": "add",
                "expire_start": "2020-05-01",
                "expire_end": "2030-05-31",
                'uid' : card2add.card_id,
                'display' :  card2add.user_name,
                'pin': card2add.card_pin,
            })
            log_add = {
                'cardsettinglog_id': (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f'),
                'cardsetting_type':'門禁群組變更',
                'user_role': '客戶',
                'user_id': card2add.user_id,
                'user_name': card2add.user_name,
                'card_id' : card2add.card_id,
                'data_origin': '' ,
                'data_new': '加入群組:%s' %(self.devicegroup_name) ,
                'cardsettinglog_time': datetime.datetime.now(),
                'cardsettinglog_user': self.env.user.name
            }
            self.env['acs.cardsettinglog'].sudo().create([log_add])

    logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
    payload={ "logid": logid, "device": [] }

    for d in self.device_ids:
        payload["device"].append({
            "device_id": d.device_id,
            "ip": d.device_ip,
            "port": d.device_port,
            "node": d.node_id,
            "card": cards
        })

    # call api to update locker's devicegroup's devices
    _logger.warning('sending request: %s' % (json.dumps(payload) ) )
    deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
    _logger.warning('deviceserver: %s' % (deviceserver) )
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
