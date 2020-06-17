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
    _rec_name = 'code'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    code = fields.Char(string="卡機編號", required=True)
    fullname = fields.Char(string="卡機名稱", required=True)
    hardware = fields.Char(string='型號', size=15, required=True)
    ip =  fields.Char(string='IP', size=15, required=True)
    port = fields.Char( string='Port',size=4, required=True)
    node = fields.Char( string='站號',size=3, required=True)
    pin = fields.Char(string='通關密碼', size=4)
    pin_update = fields.Char(string='密碼更新時間')
    status = fields.Char(string='連線否',default='')
    status_update = fields.Char(string='狀態更新時間')
    location = fields.Char(string='樓層', size=8)
    department_code = fields.Char(string='部門代號',compute='_get_department_code')
    department_id = fields.Many2one('hr.department',string='部門名稱',ondelete='set null')

    devicegroup_ids = fields.Many2many(
        string='所屬門禁群組',
        comodel_name='acs.devicegroup',
        relation='acs_devicegroup_acs_device_rel',
        column1='devicegroup_id',
        column2='device_id',
    )
    
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
        return message

    def unlink(self):
        #self.write({'devicegroup': False})
        return True
