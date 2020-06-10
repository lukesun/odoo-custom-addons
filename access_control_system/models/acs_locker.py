# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

_logger = logging.getLogger(__name__)

class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'
    _rec_name = 'locker_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    locker_status = fields.Selection([ ('閒置', '閒置'),('租用中', '租用中'),('自用', '自用'),('停用', '停用'),],'櫃位狀態', default='閒置', required=True)
    locker_id = fields.Char(string="櫃號", required=True)
    locker_type = fields.Selection([ ('倉庫', '倉庫'),('工作空間', '工作空間'),('經典車庫', '經典車庫'),('公司登記', '公司登記'),],string="租賃類別", default='倉庫', required=True)
    locker_style = fields.Char(string="類型", required=True)
    locker_spec =  fields.Char(string="規格", required=True)
    locker_floor = fields.Char(string="樓層", required=True)
    locker_vesion = fields.Char(string="期數", required=True)
    devicegroup = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')
    
    locker_owner = fields.Many2one('hr.department','所屬部門',ondelete='set null')

    card = fields.Many2one('acs.card','所屬卡片',ondelete='set null')
    contract_id = fields.Char(string="合約編號")

    # _sql_constraints = [
    #     ('unique_contract_id', 'unique(contract_id)', '合約編號不能重複！')
    #     ]
    def write(self,vals):
        _logger.warning( 'vals: %s' %(vals) )
        _logger.warning( 'self.card: %s' %(self.card) )
        if 'card' in vals:
            _logger.warning( 'card member change!!' )
            call_devices_async(self,vals)
        else:
            _logger.warning( 'card no change!!' )

        result = super(AcsLocker, self).write(vals)
        return result

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsLocker, self).unlink()
        else:
            self.write({'devicegroup': False})
            return True

#變更卡片欄位時產生合約編號
    # @api.onchange('card')
    # def _onchange_card(self):
    #     if self.card:
    #         c_id =  '%s-%s' % ( 
    #             self.locker_id ,
    #             (datetime.datetime.now() + timedelta(hours=8) ).strftime('%Y%m%d')
    #         )
    #         # record = self.env['acs.locker'].search(
    #         #     [('contract_id', 'ilike', 'c_id' )],
    #         #     order='contract_id desc',
    #         #     limit=1
    #         # ).contract_id            
    #         # _logger.warning( record )

    #     else:
    #         c_id = ''
    #     #_logger.warning( c_id )

    #     self.contract_id = c_id

def call_devices_async(self,vals):

    _logger.warning('card to remove:%s' %(self.card) )
    cards = []
    if self.card:
        cards.append({
            "event": "delete",
            'uid' : self.card.card_id,
        })
        log_del = {
            'cardsettinglog_id': (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f'),
            'cardsetting_type':'櫃位退租',
            'user_role': '客戶',
            'user_id': self.card.user_id,
            'user_name': self.card.user_name,
            'card_id' : self.card.card_id,
            'data_origin': '櫃位編號:%s' %(self.locker_id) ,
            'data_new': '',
            'cardsettinglog_time': datetime.datetime.now(),
            'cardsettinglog_user': self.env.user.name
        }
        self.env['acs.cardsettinglog'].sudo().create([log_del])
    if vals['card']:
        _logger.warning( 'add card from vals[card]: %s' %( vals['card'] ) )
        card2add = self.env['acs.card'].sudo().search([['id','=',vals['card'] ] ])
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
            'cardsetting_type':'櫃位租用',
            'user_role': '客戶',
            'user_id': card2add.user_id,
            'user_name': card2add.user_name,
            'card_id' : card2add.card_id,
            'data_origin': '' ,
            'data_new': '櫃位編號:%s' %(self.locker_id),
            'cardsettinglog_time': datetime.datetime.now(),
            'cardsettinglog_user': self.env.user.name
        }
        self.env['acs.cardsettinglog'].sudo().create([log_add])

    logid = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
    payload={ "logid": logid, "device": [] }
    if self.devicegroup:
        for d in self.devicegroup.device_ids:
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
