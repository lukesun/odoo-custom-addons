# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from .acs import write_card_log

_logger = logging.getLogger(__name__)

class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'
    _rec_name = 'uid'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    status = fields.Selection([ ('啟用', '啟用'),('作廢', '作廢'),],'卡片狀態', default='啟用', required=True)
    
    uid = fields.Char(string='卡片號碼', required=True)
    pin = fields.Char(string='卡片密碼')

    person_ref = fields.Reference( selection=[('res.partner', '客戶') , ('hr.employee', '員工'),], string='用戶')

    user_code = fields.Char(string='I D',compute='_get_user_code')
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

    partner_id = fields.Many2one('res.partner','客戶')
    
    #客戶租用櫃位清單
    contract_ids = fields.One2many('acs.contract', 'partner_id', string="合約清單")

    @api.constrains('devicegroup_ids')
    def check_devicegroup_ids(self):
        for record in self:
            if record.user_role == '客戶':
                #客戶卡片不能使用門禁群組
                for dg in record.devicegroup_ids:
                    dg.unlink()
                raise ValidationError('客戶卡片無法更改門禁群組授權')
            else:
                #非客戶卡片不能使用合約列表
                for c in record.contract_ids:
                    c.unlink()

    @api.constrains('contract_ids')
    def check_contract_ids(self):
        for record in self:
            if record.user_role == '客戶':
                #客戶卡片不能使用門禁群組
                for dg in record.devicegroup_ids:
                    dg.unlink()
            else:
                #非客戶卡片不能使用合約列表
                for c in record.contract_ids:
                    c.unlink()
                raise ValidationError('只有客戶卡片才能更改合約列表')

#for compute fields
#變更用戶欄位時顯示用戶類別
    @api.onchange('person_ref')
    def _get_owner_role(self):
        for record in self:
            _logger.warning( '_get_owner_role! %s' %( record.person_ref ) )
            if record.person_ref:
                if 'employee' in record.person_ref:
                    _logger.warning( 'employee! %s' %( record.person_ref.employee ) )
                    if (record.person_ref.employee == False):
                        if hasattr(record.person_ref,'supplier_rank') and record.person_ref.supplier_rank > 0 :
                            _logger.warning( 'supplier_rank! %s' %( record.person_ref.supplier_rank ) )
                            record.partner_id = False
                            record.user_role = '廠商'
                        else:
                            _logger.warning( 'Not supplier! %s' %( record.person_ref.supplier_rank ) )
                            record.partner_id = record.person_ref
                            record.user_role = '客戶'
                else:
                    record.partner_id = False
                    record.user_role = '員工'
            else:
                record.user_role = ''

    @api.onchange('person_ref')
    def _get_user_code(self):
        for record in self:
            if record.person_ref:
                if hasattr(record.person_ref,'vat'):
                    record.user_code = record.person_ref.vat
                else:
                    record.user_code = ''
            else:
                record.user_code = ''

    @api.onchange('person_ref')
    def _get_owner_name(self):
        for record in self:
            if record.person_ref:
                record.user_name = record.person_ref.name
            else:
                record.user_name = ''

    @api.onchange('person_ref')
    def _get_owner_phone(self):
        for record in self:
            if record.person_ref:
                if hasattr(record.person_ref,'phone'):
                    record.user_phone = record.person_ref.phone
                else:
                    record.user_phone = ''
            else:
                record.user_phone = ''
#card ORM methods
    @api.model
    def create(self, vals):
        #write_card_log(self ,vals)
        result = super(AcsCard, self).create(vals)
        return result
    
    def write(self,vals):
        #write_card_log(self ,vals)
        result = super(AcsCard, self).write(vals)
        return result

    def unlink(self):
        #write_card_log(self ,{})
        result = super(AcsCard, self).unlink()
        return result



