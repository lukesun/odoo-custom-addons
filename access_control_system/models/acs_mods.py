# -*- coding: utf-8 -*-
# models not necessary for this system this effore result in 3 weeks delay
import base64
import collections
import datetime
import hashlib
import pytz
import threading
import re

import requests
from lxml import etree
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class Department(models.Model):
    _inherit = 'hr.department'
    code = fields.Char(string="部門代碼")

class Partner(models.Model):
    _inherit = 'res.partner'
    #客戶持有的卡片
    card_ids = fields.One2many('acs.card','partner_id')
    #客戶關聯到的合約清單
    contract_ids = fields.One2many('acs.contract','partner_id')

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        if self._context.get('show_mobile') and partner.mobile:
            name = "%s ‒ %s" % (name, partner.mobile)
        if self._context.get('show_phone') and partner.phone:
            name = "%s ‒ %s" % (name, partner.phone)
        return name

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        self = self.with_user(name_get_uid or self.env.uid)
        # as the implementation is in SQL, we force the recompute of fields if necessary
        self.recompute(['display_name'])
        self.flush()
        if args is None:
            args = []
        order_by_rank = self.env.context.get('res_partner_search_mode') 
        if (name or order_by_rank) and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            from_str = from_clause if from_clause else 'res_partner'
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            fields = self._get_name_search_order_by_fields()

            query = """SELECT res_partner.id
                         FROM {from_str}
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent}
                           OR {phone} {operator} {percent}
                           OR {mobile} {operator} {percent}
                           OR {reference} {operator} {percent}
                           OR {vat} {operator} {percent})
                           -- don't panic, trust postgres bitmap
                     ORDER BY {fields} {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(from_str=from_str,
                               fields=fields,
                               where=where_str,
                               operator=operator,
                               email=unaccent('res_partner.email'),
                               phone=unaccent('res_partner.phone'),#add for search
                               mobile=unaccent('res_partner.mobile'),#add for search
                               display_name=unaccent('res_partner.display_name'),
                               reference=unaccent('res_partner.ref'),
                               percent=unaccent('%s'),
                               vat=unaccent('res_partner.vat'),)

            where_clause_params += [search_name]*5  # for email / display_name, reference ,phone , mobile
            where_clause_params += [re.sub('[^a-zA-Z0-9]+', '', search_name) or None]  # for vat
            where_clause_params += [search_name]  # for order by
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = [row[0] for row in self.env.cr.fetchall()]

            if partner_ids:
                return models.lazy_name_get(self.browse(partner_ids))
            else:
                return []
        return super(Partner, self)._name_search(name, args, operator=operator, limit=limit, name_get_uid=name_get_uid)
class AcsLocker(models.Model):
    _name = 'acs.locker'
    _description = '櫃位設定'
    _rec_name = 'code'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    status = fields.Selection([ ('閒置', '閒置'),('租用中', '租用中'),('自用', '自用'),('停用', '停用'),],string='櫃位狀態', default='閒置', required=True)
    code = fields.Char(string="櫃號", required=True)
    category = fields.Selection([ ('倉庫', '倉庫'),('工作空間', '工作空間'),('經典車庫', '經典車庫'),('公司登記', '公司登記'),],string="租賃類別", default='倉庫', required=True)
    style = fields.Selection([ ('下層櫃', '下層櫃'),('半截下層櫃', '半截下層櫃'), ] ,string="類型",default ="下層櫃", required=True)
    spec =  fields.Char(string="規格", default ="", required=True)
    floor = fields.Selection([ ('B1','B1'),('B2','B2'),('B3','B3'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13') ] ,string="樓層",default ="1", required=True)
    vesion = fields.Selection([ ('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'), ] ,string="期數",default ="1", required=True)

    devicegroup_id = fields.Many2one('acs.devicegroup','門禁群組',ondelete='set null')
    
    #department_id = fields.Many2one('hr.department','所屬部門',ondelete='set null')
    
    # partner_id = fields.Many2one('res.partner','租用客戶', ondelete='set null')

    # @api.constrains('status')
    # def onchange_status(self):
    #     for record in self:
    #         if record.partner_id:
    #             raise ValidationError('尚有租約進行中，無法改變狀態')

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     for record in self:
    #         if record.partner_id:
    #             record.status = '租用中'
    #         else:
    #             record.status = '閒置'

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsLocker, self).unlink()

class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '合約設定'
    _rec_name = 'code'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    code = fields.Char(string="合約編號", required=True)

    status = fields.Selection([ ('正常', '正常'),('停用', '停用'),('作廢', '作廢'),],'狀態', default='正常', required=True)

    locker_id = fields.Many2one('acs.locker','租用櫃位', required=True)

    partner_id = fields.Many2one('res.partner','客戶', required=True)

    card_ids = fields.Many2many(
        string='卡片清單',
        comodel_name='acs.card',
        relation='acs_contract_acs_card_rel',
        column1='card_id',
        column2='contract_id',
    )

    # @api.onchange('status')
    # def onchange_status(self):
    #     for record in self:
    #         if record.partner_id and record.locker_id and record.status=='作廢':
    #             record.locker_id.status = '閒置'
            

    def unlink(self):
        if self.confirmUnlink:
            return super(AcsContract, self).unlink()
