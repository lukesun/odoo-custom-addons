# -*- coding: utf-8 -*-
import datetime
import requests
import json
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsDevice(models.Model):
    _name = 'acs.device'
    _description = '卡機設定'

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

    def action_test(self):
        t = datetime.datetime.now()
        logid = t.strftime('%Y%m%d-%H%M-%S-%f')
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

    devicegroup_id = fields.Char(string="群組編號", required=True)
    devicegroup_name = fields.Char(string="群組名稱", required=True)

    device_ids = fields.One2many( 'acs.device','devicegroup',string="卡機清單")
    
    #card_ids = fields.One2many('acs.card', 'devicegroup', string="卡片清單")
    #TODO change to self.card_ids
    contract_ids = fields.One2many('acs.contract', 'devicegroup', string="合約清單")

    locker_ids = fields.One2many( 'acs.locker','devicegroup',string="櫃位清單")

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
            #TODO change to self.card_ids

            for c in self.contract_ids:
                card= {
                    "event": "add",
                    "uid": c.card.card_id,
                    "display": c.card.card_owner.name,
                    "pin": c.card.card_pin,
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
            #TODO change to self.card_ids
            for c in self.contract_ids:
                card= {
                    "event": "update",
                    "uid": c.card.card_id,
                    "display": c.card.card_owner.name,
                    "pin": c.card.card_pin,
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
            #TODO change to self.card_ids
            for c in self.contract_ids:
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


class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'

    card_owner = fields.Many2one( 'res.partner' , string="聯絡人")
    user_role = fields.Char(string='身份',compute='_get_owner_role')
    user_id = fields.Char(string='I D',compute='_get_owner_id')
    user_name = fields.Char(string='名稱',compute='_get_owner_name')
    user_phone = fields.Char(string='電話',compute='_get_owner_phone')
    card_id = fields.Char(string='卡片號碼', required=True)
    card_pin = fields.Char(string='卡片密碼')
    contract_ids = fields.One2many('acs.contract', 'card', string="合約清單")
    #預備新增
    #devicegroup_ids = fields.One2many('acs.devicegroup', 'card', string="所屬群組")

    def create(self, vals):
        _logger.warning('acs.card create:%s' % ( vals ) )
        #TODO: call api to add card setting
        result = super(AcsCard, self).create(vals)
        return result

    def write(self,vals):
        _logger.warning('acs.card write:%s' % ( vals ) )
        #TODO: call api to update card setting
        result = super(AcsCard, self).write(vals)
        return result
        
    def unlink(self):
        _logger.warning('acs.card unlink:%s' % ( self.card_id ) )
        #TODO: call api to delete card setting
        self.write({'card_owner': False})
        return True
    
    def _get_owner_role(self):
        for record in self:
            record_role = '未定'
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

#改為卡片vs合約的紀錄表 (one2many)
class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '櫃位出租紀錄'
    _sql_constraints = [
        ('unique_contract_id', 'unique(contract_id)', '合約編號不能重複！')
        ]

    contract_id = fields.Char(string="合約編號", required=True, readonly=True ) 
    
    contract_status = fields.Char(string='狀態')

    card = fields.Many2one('acs.card',string='所屬卡片',ondelete='set null')
    #預備新增
    #locker fields.Many2one('acs.locker',string='所屬櫃位',ondelete='set null')
    
    #預備搬到card物件
    devicegroup = fields.Many2one('acs.devicegroup','所屬門禁群組',ondelete='set null')

#依選擇的櫃位產生合約編號
    #@api.onchange('locker')
    #def _onchange_devicegroup(self):
    #    t = datetime.datetime.now()
    #    c_id = self.devicegroup.devicegroup_id + t.strftime('%Y%m%d')
    #    _logger.warning('contract_id:%s' % (c_id ) )
    #    self.contract_id=c_id
    
    def unlink(self):
        self.write({'devicegroup': False})
        return True
