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

    uid = fields.Char(string='卡片號碼', required=True)
    pin = fields.Char(string='卡片密碼')
    status = fields.Selection([ ('新建', '新建'),('啟用', '啟用'),('作廢', '作廢'),],'卡片狀態', default='新建', required=True)

    user_role = fields.Selection([ ('員工', '員工'),('客戶', '客戶'),('廠商', '廠商'),],'身份', default='客戶', required=True)
    partner_id = fields.Many2one('res.partner','持卡人', default=False)
    employee_id = fields.Many2one('hr.employee','員工', default=False)
    
    user_code = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    user_phone = fields.Char(string='電話')
    #卡片被授權進入的門禁群組
    devicegroup_ids = fields.Many2many(
        string='授權門禁群組',
        comodel_name='acs.devicegroup',
        relation='acs_devicegroup_acs_card_rel',
        column1='devicegroup_id',
        column2='card_id',
    )
    #卡片被授權的合約清單
    contract_ids = fields.Many2many(
        string='合約清單',
        comodel_name='acs.contract',
        relation='acs_contract_acs_card_rel',
        column1='contract_id',
        column2='card_id',
    )

    def action_create_contract(self):
        raise UserError('Not support yet,action_create_contract.')

    def action_get_pin(self):
        raise UserError('Not support yet,action_get_pin.')
        # for record in self:
        #     record.pin = "".join(choice(digits) for i in range(4))

    def action_uid_change(self):
        raise UserError('Not support yet,action_uid_change.')

    def action_dispose(self):
        raise UserError('Not support yet,action_dispose.')
        #text = """The case """+str(self.case_no)+""" will be forward to VC for further Approval. Are you want to proceed."""
        #query='delete from thesis_approval_message_oric'
        #self.env.cr.execute(query) 
        #value=self.env['thesis.approval.message.oric'].sudo().create({'text':text}) 
        
        return { 
            'type':'ir.actions.act_window', 
            'name':'卡片作廢',
            'res_model':'acs.card', 
            'view_type':'form', 
            'view_mode':'form', 
            'target':'new',  
            'context':{
                #'thesis_obj':self.id,
                'flag':'WHAT EVER'
            }, 
            'res_id':self.id
        }
        
    @api.onchange('user_role')
    def _change_user_role(self):
        for record in self:
            if record.status !='新建':
                raise ValidationError('已啟用的卡片無法更改持有人，請作廢或新增卡片。')
            else:
                if record.user_role == '廠商':
                    record.employee_id = False
                    return {'domain': {'partner_id': [('supplier_rank', '>', 0)]}}
                if record.user_role == '客戶':
                    record.employee_id = False
                    return {'domain': {'partner_id': [('supplier_rank', '=', 0)]}}
                if record.user_role == '員工':
                    record.partner_id = False

    @api.onchange('partner_id')
    def _update_partner_profile(self):
        for record in self:
            if record.partner_id:
                record.user_name = record.partner_id.name
                record.user_phone = record.partner_id.phone
                record.user_code = record.partner_id.vat #統編 身份證

    @api.onchange('employee_id')
    def _update_employee_profile(self):
        for record in self:
            if record.employee_id:
                record.user_name = record.employee_id.name
                record.user_phone = record.employee_id.work_phone
                record.user_code = record.employee_id.barcode #徽章 ID, 工號

#card ORM methods
    @api.model
    def create(self, vals):
        if 'status' in vals:
            if vals['status'] == '新建':
                vals['status'] ='啟用'
        write_card_log(self ,vals)
        result = super(AcsCard, self).create(vals)
        return result
    
    def write(self,vals):
        write_card_log(self ,vals)
        result = super(AcsCard, self).write(vals)
        return result

    def unlink(self):
        if self.confirmUnlink:
            write_card_log(self ,{})
            result = super(AcsCard, self).unlink()
            return result
        else:
            raise ValidationError("禁止未確認的刪除")

    # @api.constrains('devicegroup_ids')
    # def check_devicegroup_ids(self):
    #     for record in self:
    #         if record.user_role == '客戶':
    #             #客戶卡片不能使用門禁群組
    #             for dg in record.devicegroup_ids:
    #                 dg.unlink()
    #             raise ValidationError('客戶卡片無法更改門禁群組授權')
    #         else:
    #             #非客戶卡片不能使用合約列表
    #             for c in record.contract_ids:
    #                 c.unlink()

    # @api.constrains('contract_ids')
    # def check_contract_ids(self):
    #     for record in self:
    #         if record.user_role == '客戶':
    #             #客戶卡片不能使用門禁群組
    #             for dg in record.devicegroup_ids:
    #                 dg.unlink()
    #         else:
    #             #非客戶卡片不能使用合約列表
    #             for c in record.contract_ids:
    #                 c.unlink()
    #             raise ValidationError('只有客戶卡片才能更改合約列表')
