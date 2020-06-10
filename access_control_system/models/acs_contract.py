# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

_logger = logging.getLogger(__name__)

class AcsContract(models.Model):
    _name = 'acs.contract'
    _description = '設定'
    _rec_name = 'contract_id'
    confirmDelte = fields.Boolean(string='確認刪除', default=False)
