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

