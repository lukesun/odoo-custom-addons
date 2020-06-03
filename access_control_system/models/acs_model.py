# -*- coding: utf-8 -*-
import json
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'
    _rec_name = 'locker_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)

    locker_id = fields.Char(string="櫃位編號", required=True)
    locker_type = fields.Char(string="產品種類")
    locker_style = fields.Char(string="類型")
    locker_spec =  fields.Char(string="規格")
    locker_floor = fields.Char(string="樓層")
    locker_vesion = fields.Char(string="期數")
    
    locker_owner = fields.Many2one('hr.department','所屬部門',ondelete='set null')

    devicegroup = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')
    
    card = fields.Many2one('acs.card','所屬卡片',ondelete='set null')
    
    contract_id = fields.Char(string="合約編號")

    # _sql_constraints = [
    #     ('unique_contract_id', 'unique(contract_id)', '合約編號不能重複！')
    #     ]

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsLocker, self).unlink()
        else:
            self.write({'devicegroup': False})
            return True
#變更卡片欄位時產生合約編號
    @api.onchange('card')
    def _onchange_card(self):
        if self.card:
            c_id =  '%s-%s' % ( 
                self.locker_id ,
                (datetime.datetime.now() + timedelta(hours=8) ).strftime('%Y%m%d')
            )
            # record = self.env['acs.locker'].search(
            #     [('contract_id', 'ilike', 'c_id' )],
            #     order='contract_id desc',
            #     limit=1
            # ).contract_id            
            # _logger.warning( record )

        else:
            c_id = ''
        #_logger.warning( c_id )

        self.contract_id = c_id

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

    #員工廠商授權進入的門禁群組
    #devicegroup_ids = fields.One2many('acs.devicegroup', 'card', string="授權門禁群組")

    #客戶租用櫃位清單
    locker_ids = fields.One2many('acs.locker', 'card', string="合約清單")

    # def name_get(self, cr, uid, ids, context=None):
    #     if not len(ids):
    #         return []
    #     res = [(r['id'], r['name'] and '%s [%s]' % (r['name'], r['name2']) or r['name'] ) for r in self.read(cr, uid, ids, ['name', 'name2'], context=context) ]
    #     return res

    @api.model
    def create(self, vals):
        _log2table(self ,'新增' ,vals)
        #TODO: call api to add card setting
        result = super(AcsCard, self).create(vals)
        return result
    
    def write(self,vals):
        _log2table(self ,'修改' ,vals)
        #TODO: call api to update card setting
        result = super(AcsCard, self).write(vals)
        return result

    def unlink(self):
        _log2table(self ,'刪除' ,{})

        #TODO: call api to delete card setting
        result = super(AcsCard, self).unlink()
        return result
    
    def _get_owner_role(self):
        for record in self:
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

def _log2table(self ,cardsetting_type ,vals):
    _logger.warning( cardsetting_type )
    _logger.warning( vars(self) )
    _logger.warning( vals )
    cardsettinglog_id = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y%m%d-%H%M-%S-%f')
    ldata = {
        'cardsettinglog_id': cardsettinglog_id,
        'cardsetting_type':cardsetting_type,
        'user_role': '客戶',
        'user_id': '',
        'user_name': '',
        'card_id' : '',
        'data_origin': '' ,
        'data_new': json.dumps(vals),
        'cardsettinglog_time': datetime.datetime.now(),
        'cardsettinglog_user': self.env.user.name
    }

    #use new overwrite old
    for record in self:
        vals_old ={
            'user_role': record.user_role,
            'user_id': record.user_id, 
            'user_name': record.user_name,
            'card_id' : record.card_id,
            'card_pin' : record.card_pin,
        }
        ldata['user_role'] =record.user_role
        ldata['user_id'] =record.user_id
        ldata['user_name'] =record.user_name
        ldata['card_id'] = record.card_id

        ldata['data_origin'] =json.dumps(vals_old)

    if hasattr(vals,'card_id'):
        ldata['card_id'] = vals.card_id

    self.env['acs.cardsettinglog'].sudo().create([ldata])

    if hasattr(vals,'card_pin'):
        ldata['cardsetting_type'] = '變更密碼'
        self.env['acs.cardsettinglog'].sudo().create([ldata])


