# -*- coding: utf-8 -*-
import json
import requests

import datetime
from datetime import timedelta, date

from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsDevice(models.Model):
    _name = 'acs.device'
    _description = '卡機設定'
    _rec_name = 'device_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    device_id = fields.Char(string="卡機編號", required=True)
    name = fields.Char(string="卡機名稱", required=True)
    device_ip =  fields.Char(string='IP 位址', size=15, required=True)
    device_type = fields.Char(string='型號', size=15, required=True)
    device_port = fields.Char( string='卡機Port',size=4, required=True)
    node_id = fields.Char( string='卡機站號',size=3, required=True)
    device_location = fields.Char(string='樓層', size=8)
    device_pin = fields.Char(string='通關密碼', size=4)
    device_pin_update = fields.Char(string='密碼更新時間')

    device_owner = fields.Many2one('hr.department',string='所屬門市(部門)',ondelete='set null')

    devicegroup = fields.Many2one('acs.devicegroup',string='門禁群組',ondelete='set null')

    def action_reset_pincode(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        payload={
            "logid": logid, 
            "device": [
                {
                "ip": self.device_ip,
                "port": self.device_port,
                "node": self.node_id
                }
            ]
        }
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )
        r = requests.post(deviceserver+'/api/device-test',data=json.dumps(payload))
        message = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
            'title': r.status_code,
            'message': r._content,
            'sticky': True,
            }
        }
        return message
    def action_test(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        payload={
            "logid": logid, 
            "device": [
                {
                "ip": self.device_ip,
                "port": self.device_port,
                "node": self.node_id
                }
            ]
        }
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )

        r = requests.post(deviceserver+'/api/device-test',data=json.dumps(payload))
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
        return message

    def unlink(self):
        self.write({'devicegroup': False})
        return True

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

    def action_push(self):
        t = datetime.datetime.now()
        logid = t.strftime('%Y%m%d-%H%M-%S-%f')

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
        return message


    def action_update(self):
        t = datetime.datetime.now()
        logid = t.strftime('%Y%m%d-%H%M-%S-%f')

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
                    "expire_start": "2020-05-01",
                    "expire_end": "2020-05-31"
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
        return message

    def action_clear(self):
        t = datetime.datetime.now()
        logid = t.strftime('%Y%m%d-%H%M-%S-%f')

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
                    "uid": c.card.card_id,
                }
                device["card"].append(card)

            payload["device"].append(device)
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )

        r = requests.post( deviceserver + '/api/devices-async' ,data=json.dumps(payload))
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
        return message



