# -*- coding: utf-8 -*-
import json
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'
    _rec_name = 'card_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    card_owner = fields.Many2one( 'res.partner' , string="聯絡人")
    card_id = fields.Char(string='卡片號碼', required=True)
    card_pin = fields.Char(string='卡片密碼')

    user_id = fields.Char(string='I D',compute='_get_owner_id')
    user_name = fields.Char(string='名稱',compute='_get_owner_name')
    user_phone = fields.Char(string='電話',compute='_get_owner_phone')
    user_role = fields.Char(string='身份',compute='_get_owner_role')

    #員工廠商授權進入的門禁群組 改Many2many
    devicegroup_ids = fields.Many2many(
        string='授權門禁群組',
        comodel_name='acs.devicegroup',
        relation='acs_devicegroup_acs_card_rel',
        column1='devicegroup_id',
        column2='card_id',
    )
    
    #客戶租用櫃位清單
    locker_ids = fields.One2many('acs.locker', 'card', string="合約清單",readonly=True)

#for compute fields
    def _get_owner_role(self):
        for record in self:
            record_role = ''
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

#card ORM methods
    def create(self, vals):
        _log2table(self ,'新增' ,vals)
        result = super(AcsCard, self).create(vals)
        return result
    
    def write(self,vals):
        _log2table(self ,'修改' ,vals)
        result = super(AcsCard, self).write(vals)
        return result

    def unlink(self):
        _log2table(self ,'刪除' ,{})
        result = super(AcsCard, self).unlink()
        return result


def _log2table(self ,cardsetting_type ,vals):

    _logger.warning( cardsetting_type )
    _logger.warning( self )
    _logger.warning( 'vals:' + json.dumps(vals) )

    ldata = {
        'cardsettinglog_id': '',
        'cardsetting_type':cardsetting_type,
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
            'user_id': record.user_id, 
            'user_name': record.user_name,
            'card_id' : record.card_id,
            'card_pin' : record.card_pin,
        }
        #use old vals for display
        ldata['user_role'] =record.user_role
        ldata['user_id'] =record.user_id
        ldata['user_name'] =record.user_name

        ldata['card_id'] = record.card_id
        ldata['data_origin'] =json.dumps(vals_old)

        #TODO: build 1 request for api/devices-async
        # 1: get ORM 1 card object--> 1 relate locker group + authorized groups --> relate devices
        # 2: set params from card object CRUD operations following up
        # 3: send request after log into logtable

        #use new overwrite display cols when changing card_id
        if 'card_id' in vals:
            _logger.warning( 'card_id change!' )
            ldata['card_id'] = vals['card_id']
            ldata['cardsetting_type'] = '變更卡號'
            #TODO 1 build delete + addnew api request
            _logger.warning( 'card_id changed!' )
        else:
            _logger.warning( 'card_id no change!' )
            #TODO 2 build addnew api request
        
        if 'card_pin' in vals:
            #TODO 3 build update api request
            _logger.warning( 'card_pin change!' )
            ldata['cardsetting_type'] = '變更密碼'
        else:
            _logger.warning( 'card_pin no change!' )

        ldata['cardsettinglog_id'] = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
        self.env['acs.cardsettinglog'].sudo().create([ldata])
        _logger.warning( ldata )

    #for addnew--> not update or delete
    if recordcount == 0:
        for val in vals:
            recordcount+=1
            if 'card_id' in val:
                _logger.warning( 'new card_id!' + str(recordcount) )
                ldata['card_id'] = val['card_id']
                #TODO build add api request
                ldata['cardsettinglog_id'] = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
                self.env['acs.cardsettinglog'].sudo().create([ldata])
                _logger.warning( ldata )
            else:
                _logger.warning( 'cannot add without card_id!' + str(recordcount))

    #TODO send request to /api/devices-async
    _logger.warning( 'begin send reuest:' )
