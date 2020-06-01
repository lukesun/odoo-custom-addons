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
    @http.route('/api/devices-async-result/',  auth='public', methods=["POST"], csrf=False)
    def async_result(self, **kw):
        _logger.warning( kw )
        return http_log_response('OK')

    @http.route('/api/device-test-result/', auth='public', methods=["POST"], csrf=False)
    def test_result(self, **kw):
        _logger.warning( kw )
        return http_log_response('OK')

    @http.route('/api/device-record/', auth='public', methods=["POST"], csrf=False)
    def device_reocrd(self, **kw):
        _logger.warning( kw )
        return http_log_response('OK')
    
    @http.route('/api/devices-query', auth='public', methods=["POST"], csrf=False)
    def devices_query(self, **kw):
        _logger.warning( kw )
        devices = request.env['acs.device'].search([])

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
            _logger.warning( 'ip:%s,port:%s,node_id:%s,status:%s,pin:%s' 
            % (d['ip'],d['node'],d['port'],d['status'],d['pin'])  )
            dr = http.request.env['acs.device'].search([['device_ip','=',d['ip'] ],['device_port','=',d['port'] ]])
            #_logger.warning( dr.mapped['device_port'] )
            if dr :
                _logger.warning( 'name:%s' % (dr.name) )
                if d['status'] == '1':
                    dr.device_pin = d['pin']
                    t = datetime.datetime.now()
                    dr.device_pin_update = t.strftime('%Y-%m-%d %H:%M:%S')
            else:
                _logger.warning( 'no match!' )

        return http_log_response('OK')

