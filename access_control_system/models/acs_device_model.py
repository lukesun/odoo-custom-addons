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
    device_ip =  fields.Char(string='IP 位址', size=15)
    device_type = fields.Char(string='型號', size=15)
    device_port = fields.Char( string='卡機Port',size=4)
    node_id = fields.Char( string='卡機站號',size=3)
    device_location = fields.Char(string='樓層', size=8)

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

            for c in self.contract_ids:
                card= {
                    "event": "delete",
                    "uid": c.card.card_id,
                }
                device["card"].append(card)

            payload["device"].append(device)
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
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

    def _get_owner_role(self):
        for record in self:
            record_role = ''
            
            if (not record.card_owner.customer_rank and not record.card_owner.supplier_rank):
                record_role = '未定'
            elif (not record.card_owner.customer_rank):
                record_role = '廠商'
            elif (not record.card_owner.supplier_rank):
                record_role = '客戶'

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

class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '合約設定'
    #_sql_constraints = [
    #    ('unique_contract_id', 'unique(contract_id)', '合約編號不能重複！')
    #    ]
    contract_id = fields.Char(string="合約編號", required=True) 
    
    contract_status = fields.Char(string='狀態')

    card = fields.Many2one('acs.card',string='所屬卡片',ondelete='set null')

    devicegroup = fields.Many2one('acs.devicegroup','所屬門禁群組',ondelete='set null')

    #def create(self, vals):
        #stage_obj = self.env['project.task.type']
        #result = super(Project, self).create(vals)
        #for resource in result.stage_ids:
        #    stage_id = stage_obj.search([('id', '=',resource.name.id)])
        #    if stage_id:
        #        stage_id.write({'project_ids': [( 4, result.id)]})
        #return result
    #def write(self,values):
        #campus_write = super(Campus,self).write(values)
        #return campus_write
    
    def unlink(self):
        self.write({'devicegroup': False})
        return True
