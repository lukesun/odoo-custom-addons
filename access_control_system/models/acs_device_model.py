# -*- coding: utf-8 -*-
import datetime
import requests
import json
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

#class AcsCardOwner(models.Model):
#    _name = 'acs.cardowner'
#    _description = '卡片所有人'
#    _inherit = 'res.partner'

#    @api.model
#    def name_search(self, name='', args=None, operator='ilike', limit=100):
#        if self._context.get('search_by_vat', False):
#            if name:
#                args = args if args else []
#                args.extend(['|', ['name', 'ilike', name], ['vat', 'ilike', name]])
#                name = ''
#        return super(AcsCardOwner, self).name_search(name=name, args=args, operator=operator, limit=limit)

class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'

    locker_id = fields.Char(string="櫃位編號", required=True)
    locker_type = fields.Char(string="產品種類")
    locker_style = fields.Char(string="類型")
    locker_spec =  fields.Char(string="規格")
    locker_floor = fields.Char(string="樓層")
    locker_vesion = fields.Char(string="期數")

    locker_owner = fields.Many2one('hr.department','所屬部門',ondelete='set null')

    devicegroup = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')

    def unlink(self):
        self.write({'devicegroup': False})
        return True
 
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
            record_role = '未知'
            #if record.card_owner.customer_rank:
            #    record_role = '客戶'
            #if record.card_owner.supplier_rank:
            #    record_role = '廠商'
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
    _sql_constraints = [
        ('contract_id', 'unique(contract_id)', '合約編號不能重複！')
        ]
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

class AcsDeviceAccesscode(models.Model):
    _name = 'acs.deviceaccesscode'
    _description = '群組通關密碼'

    devicegroup_id = fields.Char(string="通用群組", required=True)
    devicegroup_name = fields.Char(string="群組名稱", required=True)
    accesscode = fields.Char(string="通關密碼", required=True)
    start_time = fields.Datetime(string='有效日期', required=True)
    end_time = fields.Datetime(string='失效日期')

class AcsServicelog(models.Model):
    _name = 'acs.servicelog'
    _description = '卡機通訊紀錄'
    #devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
    

class AcsConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    deviceserver = fields.Char(string='卡機伺服器網址')
    def _onchange_deviceserver(self):
        if not self.deviceserver:
            self.deviceserver = "http://odooerp.morespace.com.tw:9090"

    def get_values(self):
        res = super(AcsConfigSettings, self).get_values()
        res.update(
            deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        )
        return res

    def set_values(self):
        super(AcsConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('acs.deviceserver', self.use_security_lead)

class AcsCardlog(models.Model):
    _name = 'acs.cardlog'
    _description = '刷卡紀錄'

    cardlog_id = fields.Char(string='紀錄編號')
    device_owner = fields.Char(string='門市')
    device_name = fields.Char(string='卡機名稱')
    user_role = fields.Char(string='身份')
    card_id = fields.Char(string='卡片號碼')
    cardlog_type = fields.Char(string='卡別')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    cardlog_time = fields.Datetime(string='刷卡時間')
    cardlog_result = fields.Char(string='刷卡狀態')

class AcsEmployeeCardlog(models.Model):
    _name = 'acs.employeecardlog'
    _description = '員工打卡紀錄'

    employeecardlog_id = fields.Char(string='紀錄編號')
    device_owner = fields.Char(string='門市')
    device_name = fields.Char(string='卡機名稱')
    card_id = fields.Char(string='卡片號碼')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    employeecardlog_type = fields.Char(string='刷卡狀態')
    employeecardlog_time = fields.Datetime(string='刷卡時間')

class AcsCardSettinglog(models.Model):
    _name = 'acs.cardsettinglog'
    _description = '卡片異動紀錄'

    cardsettinglog_id = fields.Char(string='紀錄編號')
    cardsetting_type = fields.Char(string='異動別')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    card_id = fields.Char(string='卡片號碼')
    cardsettinglog_time = fields.Datetime(string='變更時間')
    cardsettinglog_user = fields.Char(string='變更者')    

class AcsAccessCodelog(models.Model):
    _name = 'acs.accesscodelog'
    _description = '個人通關密碼設定紀錄'

    accesscodelog_id = fields.Char(string='紀錄編號')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    devicegroup_name = fields.Char(string='門禁群組')
    create_time = fields.Datetime(string='變更時間')
    expire_time = fields.Datetime(string='有效時間')
    accesscode = fields.Char(string='通關密碼')    
