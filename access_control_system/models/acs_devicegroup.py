# -*- coding: utf-8 -*-
import json
import requests

import datetime
from datetime import timedelta, date

from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

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
                "expire_start": "2030-05-01",
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

class AcsDeviceGroup(models.Model):
    _name = 'acs.devicegroup'
    _description = '門禁群組設定'
    _rec_name = 'devicegroup_name'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    devicegroup_id = fields.Char(string="群組編號", required=True)
    devicegroup_name = fields.Char(string="群組名稱", required=True)

    device_ids = fields.One2many( 'acs.device','devicegroup',string="卡機清單" ,readonly=True)
    
    #櫃位清單
    locker_ids = fields.One2many( 'acs.locker','devicegroup',string="櫃位清單" ,readonly=True)

    #授權卡片清單
    card_ids = fields.Many2many(
        string='授權卡片清單',
        comodel_name='acs.card',
        relation='acs_devicegroup_acs_card_rel',
        column1='card_id',
        column2='devicegroup_id',
    )

    def write(self,vals):
        #_logger.warning( 'vals: %s' %(vals) )
        if 'card_ids' in vals:
            _logger.warning( 'card member change!!' )            
            call_devices_async(self,vals)
        else:
            _logger.warning( 'card no change!!' )

        result = super(AcsDeviceGroup, self).write(vals)
        return result

    def action_push(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')

        payload={ "logid": logid, "device": [] }

        for d in self.device_ids: 
            device={
                "device_id": d.device_id,
                "ip": d.device_ip,
                "port": d.device_port,
                "node": d.node_id,
                "card": []
            }

            for c in self.card_ids:
                card= {
                    "event": "add",
                    "uid": c.card_id,
                    "display": c.card_owner.name,
                    "pin": c.card_pin,
                    "expire_start": "2020-05-01",
                    "expire_end": "2020-05-31"
                }
                device["card"].append(card)
            for locker in self.locker_ids:
                card= {
                    "event": "add",
                    "uid": locker.card.card_id,
                    "display": locker.card.card_owner.name,
                    "pin": locker.card.card_pin,
                    "expire_start": "2030-05-01",
                    "expire_end": "2030-05-31"
                }
                device["card"].append(card)
            payload["device"].append(device)
        
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )

        r = requests.post(deviceserver+'/api/devices-async',data=json.dumps(payload))
        _logger.warning('%s, %s' % (logid, json.dumps(payload) ) )
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


    def action_update(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')

        payload={ "logid": logid, "device": [] }

        for d in self.device_ids: 
            device={
                "device_id": d.device_id,
                "ip": d.device_ip,
                "port": d.device_port,
                "node": d.node_id,
                "card": []
            }

            for c in self.card_ids:
                card= {
                    "event": "update",
                    "uid": c.card_id,
                    "display": c.card_owner.name,
                    "pin": c.card_pin,
                    "expire_start": "2030-05-01",
                    "expire_end": "2030-05-31"
                }
                device["card"].append(card)
            for locker in self.locker_ids:
                card= {
                    "event": "update",
                    "uid": locker.card.card_id,
                    "display": locker.card.card_owner.name,
                    "pin": locker.card.card_pin,
                    "expire_start": "2030-05-01",
                    "expire_end": "2030-05-31"
                }
                device["card"].append(card)
            payload["device"].append(device)
        
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )

        r = requests.post(deviceserver+'/api/devices-async',data=json.dumps(payload))
        _logger.warning('%s, %s' % (logid, json.dumps(payload) ) )
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

    def action_clear(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')

        payload={ "logid": logid, "device": []}

        for d in self.device_ids: 
            device={
                "device_id": d.device_id,
                "ip": d.device_ip,
                "port": d.device_port,
                "node": d.node_id,
                "card": []
            }
            for c in self.card_ids:
                card= {
                    "event": "delete",
                    "uid": c.card_id,
                }
                device["card"].append(card)
            for locker in self.locker_ids:
                card= {
                    "event": "delete",
                    "uid": locker.card.card_id,
                }
                device["card"].append(card)
            payload["device"].append(device)
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        
        _logger.warning('deviceserver: %s' % (deviceserver) )
        _logger.warning('%s, %s' % (logid, json.dumps(payload) ) )
        r = requests.post( deviceserver + '/api/devices-async' ,data=json.dumps(payload))
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

    def action_reset_group_pincode(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        payload={
            "logid": logid,
            "device": []
        }
        for d in self.device_ids:
            payload['device'].append({
                "ip": d.device_ip,
                "port": d.device_port,
                "node": d.node_id
                })
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )
        _logger.warning('%s, %s' % (logid, json.dumps(payload) ) )
        r = requests.post(deviceserver+'/api/devices-update-pincode',data=json.dumps(payload))
            
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



