# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

_logger = logging.getLogger(__name__)

class AcsDevice(models.Model):
    _name = 'acs.device'
    _description = '卡機設定'
    _rec_name = 'code'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    code = fields.Char(string="卡機編號", required=True)
    fullname = fields.Char(string="卡機名稱", required=True)
    hardware = fields.Selection([ ('Soyal', 'Soyal'), ] ,string='型號', required=True)
    ip =  fields.Char(string='IP', size=15, required=True)
    port = fields.Char( string='Port',size=4, required=True)
    node = fields.Char( string='站號',size=3, required=True)
    pin = fields.Char(string='通關密碼', size=4)
    pin_update = fields.Char(string='密碼更新時間')
    status = fields.Char(string='連線否',default='')
    status_update = fields.Char(string='狀態更新時間')
    location = fields.Selection([ ('B1','B1'),('B2','B2'),('B3','B3'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13') ] ,string="樓層",default ="1", required=True)
    
    department_code = fields.Char(string='部門代號',compute='_get_department_code')
    department_id = fields.Many2one('hr.department',string='部門名稱',ondelete='set null')

    devicegroup_ids = fields.Many2many(
        string='所屬門禁群組',
        comodel_name='acs.devicegroup',
        relation='acs_devicegroup_acs_device_rel',
        column1='devicegroup_id',
        column2='device_id',
    )
    
    devicerecord_ids = fields.One2many('acs.devicerecord','device_id')

    #變更部門欄位時顯示部門代碼
    @api.onchange('department_id')
    def _get_department_code(self):
        for record in self:
            self.department_code = ''
            if record.department_id:
                self.department_code = record.department_id.code
                

    def action_reset_pincode(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        payload={
            "logid": logid, 
            "device": [
                {
                "device_id": self.code,
                "ip": self.ip,
                "port": self.port,
                "node": self.node
                }
            ]
        }
        deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        _logger.warning('deviceserver: %s' % (deviceserver) )
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
    def action_test(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        payload={
            "logid": logid, 
            "device": [
                {
                "device_id": self.code,
                "ip": self.ip,
                "port": self.port,
                "node": self.node
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
        if r.status_code != requests.codes.ok:
            message['params']['message'] = 'something goes wrong'
        else:
            self.status = 'ok'
        return message

    def unlink(self):
        #self.write({'devicegroup': False})
        return True

class AcsDeviceRecord(models.Model):
    _name = 'acs.devicerecord'
    _description = '卡機暫存'
    _rec_name = 'uid'

    device_id = fields.Many2one('acs.device',string='卡機')
    card_id = fields.Many2one('acs.card',string='卡片')
    uid = fields.Char(string='卡號')
    pin = fields.Char(string='通關密碼', size=4)
    display = fields.Char(string='顯示名稱')

    @api.model
    def create(self, vals):
        _logger.warning('devicerecord create self: %s' % (self) )
        _logger.warning('devicerecord create vals: %s' % (vals) )
        # cards2add=[]
        # cards2add.append({ 
        #         "event": "add",
        #         "expire_start": "2020-05-01",
        #         "expire_end": "2030-05-31",
        #         'uid' : vals['uid'],
        #         'display' : vals['display'],
        #     })
        result = super(AcsDeviceRecord, self).create(vals)
        return result

    def write(self,vals):
        _logger.warning('devicerecord write self: %s' % (self) )
        _logger.warning('devicerecord write vals: %s' % (vals) )
        for record in self:
            _logger.warning('devicerecord write record: %s' % (record) )
            # cards2update = []
            # cards2update.append({ 
            #     "event": "update",
            #     "expire_start": "2020-05-01",
            #     "expire_end": "2030-05-31",
            #     'uid' : vals['uid'],
            #     'display' :  vals['display'],
            #     'pin': vals['pin'],
            # })            
            result = super(AcsDeviceRecord, self).write(vals)
            return result

    def unlink(self):
        _logger.warning('devicerecord unlink self: %s' % (self) )
        # cards2delete =[]
        # cards2delete.append({
        #         "event": "delete",
        #         'uid' : self.uid,
        #     })
        result = super(AcsDeviceRecord, self).unlink()
        return result
