# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

_logger = logging.getLogger(__name__)

class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'
    _rec_name = 'uid'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    partner_id = fields.Many2one( 'res.partner' , string="聯絡人")

    uid = fields.Char(string='卡片號碼', required=True)
    pin = fields.Char(string='卡片密碼')

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
    
    #客戶租用櫃位清單
    #contract_ids = fields.One2many('acs.contract', 'partner_id', string="合約清單")

#for compute fields
    def _get_owner_role(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.customer_rank:
                    if record.partner_id.customer_rank > 0:
                        record.user_role = '客戶'
                    else:
                        if record.partner_id.employee:
                            record.user_role = '員工'
                        else:
                            if record.partner_id.supplier_rank:
                                if record.partner_id.supplier_rank > 0:
                                    record.user_role = '廠商'

    def _get_user_code(self):
        for record in self:
            record.user_code = record.partner_id.vat

    def _get_owner_name(self):
        for record in self:
            record.user_name = record.partner_id.name

    def _get_owner_phone(self):
        for record in self:
            record.user_phone = record.partner_id.phone

#card ORM methods
    @api.model
    def create(self, vals):
        _log2table(self ,vals)
        result = super(AcsCard, self).create(vals)
        return result
    
    def write(self,vals):
        _log2table(self ,vals)
        result = super(AcsCard, self).write(vals)
        return result

    def unlink(self):
        _log2table(self ,{})
        result = super(AcsCard, self).unlink()
        return result



