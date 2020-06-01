# -*- coding: utf-8 -*-
import json
import logging
import requests
import datetime

from odoo import http

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
        return http_log_response('OK')

    @http.route('/api/devices-update', auth='public', methods=["POST"], csrf=False)
    def device_update(self, **kw):
        _logger.warning( kw )
        return http_log_response('OK')

