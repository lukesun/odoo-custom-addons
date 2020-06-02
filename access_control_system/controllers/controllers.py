# -*- coding: utf-8 -*-
import json
import logging
import datetime
import math

from odoo import http, _, exceptions
from odoo.http import request

_logger = logging.getLogger(__name__)

def http_log_response(msg):
    t = datetime.datetime.now()
    logid = t.strftime('%Y%m%d-%H%M-%S-%f')
    res = {
        "logid": logid,
        "desc": msg
    }
    return http.Response(json.dumps(res),status=200,mimetype='application/json')

class AcsAPI(http.Controller):
    @http.route('/api/devices-async-result/',  auth='public', methods=["POST"], csrf=False,type='http')
    def async_result(self, **kw):
        _logger.warning( kw )
        return http_log_response('OK')

    @http.route('/api/device-test-result/', auth='public', methods=["POST"], csrf=False,type='http')
    def test_result(self, **kw):
        _logger.warning( kw )
        return http_log_response('OK')

    @http.route('/api/device-record/', auth='public', methods=["POST"], csrf=False,type='http')
    def device_reocrd(self, **kw):
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
                    if d.device_owner.suppleir_rank:
                        ldata['user_role'] = '廠商'
                    if d.device_owner.customer_rank:
                        ldata['user_role'] = '客戶'

        cards = http.request.env['acs.card'].sudo().search([['card_id','=',dl['card_uid'] ] ])
        if cards :
            for c in cards:
                ldata['user_id'] = c.card_owner.vat
                ldata['user_name'] = c.card_owner.name

        http.request.env['acs.cardlog'].sudo().create([ldata])
        _logger.warning('/api/device-record: log-->%s' % ( json.dumps(ldata) ) )
        return http_log_response('OK')
    
    @http.route('/api/devices-query', auth='public', methods=["POST"], csrf=False,type='http')
    def devices_query(self, **kw):
        _logger.warning( kw )
        devices = request.env['acs.device'].sudo().search([])

        payload=[]

        for d in devices: 
            device={
                "device_id": d.device_id,
                "ip": d.device_ip,
                "port": d.device_port,
                "node": d.node_id,
            }
            payload.append(device)
        
        _logger.warning('/api/devices-query: %s' % (json.dumps(payload) ) )
        return http.Response(json.dumps(payload),status=200,mimetype='application/json')

    @http.route('/api/device-update', auth='public', methods=["POST"], csrf=False,type='http')
    def device_update(self, **kw):

        _logger.warning('/api/device-update: %s' % ( request.httprequest.data ) )

        payload = json.loads(request.httprequest.data)
        for d in payload['device']:

            dr = http.request.env['acs.device'].sudo().search(
                [['device_ip','=',d['ip'] ],['device_port','=',d['port'] ]])

            if dr :
                _logger.warning( 'device name:%s' % (dr.name) )
                if d['status'] == '1':
                    dr.device_pin = d['pin']
                    t = datetime.datetime.now()
                    dr.device_pin_update = t.strftime('%Y-%m-%d %H:%M:%S')
                
                return http_log_response('OK')
            else:
                _logger.warning( 'no match!' )
                return http_log_response('no match!')
