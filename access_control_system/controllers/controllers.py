# -*- coding: utf-8 -*-
import json
import logging
import datetime
from datetime import timedelta, date
from odoo import http, _, exceptions
from odoo.http import request

_logger = logging.getLogger(__name__)

def http_log_response(msg):
    #now = ( datetime.datetime.now() + timedelta(hours=8) ).strftime("%c")
    t = datetime.datetime.now()
    logid = t.strftime('%Y%m%d-%H%M-%S-%f')
    res = {
        "logid": logid,
        "desc": msg
    }
    return http.Response(json.dumps(res),status=200,mimetype='application/json')

class AcsAPI(http.Controller):

#多部卡機設定的非同步更新結果
    @http.route('/api/devices-async-result/',  auth='public', methods=["POST"], csrf=False,type='http')
    def async_result(self, **kw):

        return http_log_response('OK')

#多筆卡機的非同步連線測試結果
    @http.route('/api/device-test-result/', auth='public', methods=["POST"], csrf=False,type='http')
    def test_result(self, **kw):

        return http_log_response('OK')

#每次使用者刷卡或輸入密碼後卡關送過來的資料
    @http.route('/api/device-record/', auth='public', methods=["POST"], csrf=False,type='http')
    def device_reocrd(self, **kw):
        _logger.warning( ( datetime.datetime.now() + timedelta(hours=8) ).strftime("%c") )
        _logger.warning('/api/device-record: %s' % ( request.httprequest.data ) )
        dl = json.loads(request.httprequest.data)
        #0-上班, 1-下班, 2-加班上, 3-加班下, 4-午休出, 5-午休回, 6-外出, 7-返回
        cardlog_type = {
            '0':'上班',
            '1':'下班',
            '2':'加班上',
            '3':'加班下',
            '4':'午休出',
            '5':'午休回',
            '6':'外出',
            '7':'返回',
        }
        #0B-刷卡成功, 03-卡號不存在, 01-輸入密碼錯誤, 1C-密碼正確, 06-卡號過期
        cardlog_result= {
            '0B':'刷卡成功',
            '03':'卡號不存在',
            '01':'輸入密碼錯誤',
            '1C':'密碼正確',
            '06':'卡號過期',
        }
        ldata = {
            'cardlog_id': str(dl['id']),
            'device_owner':'',
            'device_name': '',
            'user_role': '',
            'card_id':dl['card_uid'],
            'cardlog_type':cardlog_type[ dl['type'] ] ,
            'user_id': '',
            'user_name': '',
            'cardlog_time' : dl['date'] + ' ' + dl['time'],
            'cardlog_result': cardlog_result[ dl['function_code'] ] ,
            'cardlog_data': dl['source_data'],
            }
        devices = http.request.env['acs.device'].sudo().search(
            [['device_ip','=',dl['ip'] ],['node_id','=',dl['node_id'] ]])

        if devices :
            for d in devices:
                ldata['device_name'] = d.name
                if d.device_owner:
                    ldata['device_owner'] = d.device_owner.name

        cards = http.request.env['acs.card'].sudo().search([['card_id','=',dl['card_uid'] ] ])
        if cards :
            for c in cards:
                ldata['user_id'] = c.card_owner.vat
                ldata['user_name'] = c.card_owner.name
                _logger.warning('/api/device-record: card_owner.name-->%s' % ( ldata['user_name'] ) )
                if hasattr(c.card_owner,'suppleir_rank') and c.card_owner.suppleir_rank>0:
                    ldata['user_role'] = '廠商'
                    _logger.warning('/api/device-record: suppleir_rank-->%s' % ( c.card_owner.suppleir_rank ) )
                if hasattr(c.card_owner,'customer_rank') and c.card_owner.customer_rank>0:
                    ldata['user_role'] = '客戶'
                    _logger.warning('/api/device-record: customer_rank-->%s' % ( c.card_owner.customer_rank ) )

        http.request.env['acs.cardlog'].sudo().create([ldata])
        _logger.warning('/api/device-record: log-->%s' % ( json.dumps(ldata) ) )
        return http_log_response('OK')

#取所有有效卡機(基本資料)
    @http.route('/api/devices-query', auth='public', methods=["POST"], csrf=False,type='http')
    def devices_query(self, **kw):

        devices = request.env['acs.device'].sudo().search([])

        payload=[]

        for d in devices:
            if d.devicegroup: #有被歸到門禁群組才算有效
                device={
                    "device_id": d.device_id,
                    "ip": d.device_ip,
                    "port": d.device_port,
                    "node": d.node_id,
                }
                payload.append(device)
        
        _logger.warning('/api/devices-query: %s' % (json.dumps(payload) ) )
        return http.Response(json.dumps(payload),status=200,mimetype='application/json')

#卡機通關密碼更新通知 (群組密碼)
    @http.route('/api/device-update', auth='public', methods=["POST"], csrf=False,type='http')
    def device_update(self, **kw):

        _logger.warning('/api/device-update: %s' % ( request.httprequest.data ) )

        payload = json.loads(request.httprequest.data)
        for d in payload['device']:

            dr = http.request.env['acs.device'].sudo().search(
                [['device_ip','=',d['ip'] ],['device_port','=',d['port'] ]])
            _logger.warning( 'device ip:%s,port:%s' % (dr.name,d['port']) )

            if dr :
                _logger.warning( 'device name:%s' % (dr.name) )
                if d['status'] == '1':
                    dr.device_pin = d['pin']
                    t = datetime.datetime.now()
                    dr.device_pin_update = t.strftime('%Y-%m-%d %H:%M:%S')
                    _logger.warning( 'update ok' )
                else:
                    _logger.warning( 'disconnect!' )
            else:
                _logger.warning( 'config not exist!' )

        return http_log_response('OK')
