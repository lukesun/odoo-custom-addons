# -*- coding: utf-8 -*-
import json
import requests

import datetime
from datetime import timedelta, date

from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsDeviceGroup(models.Model):
    _name = 'acs.devicegroup'
    _description = '門禁群組設定'
    _rec_name = 'code'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    code = fields.Char(string="群組編號", required=True)
    fullname = fields.Char(string="群組名稱", required=True)

    #櫃位清單
    locker_ids = fields.One2many( 'acs.locker','devicegroup_id',string="櫃位清單" ,readonly=True)

    #卡機清單
    device_ids = fields.Many2many(
        string='卡機清單',
        comodel_name='acs.device',
        relation='acs_devicegroup_acs_device_rel',
        column1='device_id',
        column2='devicegroup_id',
    )

    #授權卡片清單
    card_ids = fields.Many2many(
        string='卡片清單',
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
    
    #更新所屬卡機的通關密碼
    def action_reset_group_pincode(self):
        logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        payload={
            "logid": logid,
            "device": []
        }
        for d in self.device_ids:
            payload['device'].append({
                "device_id": d.codename,
                "ip": d.ip,
                "port": d.port,
                "node": d.node
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

