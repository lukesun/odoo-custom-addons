# -*- coding: utf-8 -*-
import json
import logging
import requests

from odoo import http

def http_log_response(logid , msg):
    res = {
        "logid": logid,
        "desc": msg
    }
    return http.Response(json.dumps(res),status=200,mimetype='application/json')

class AcsAPI(http.Controller):
    @http.route('/api/devices-async-result/',  auth='public', methods=["POST"], csrf=False)
    def devices(self, **kw):
        return http_log_response('devices-async-result', 'OK')

    @http.route('/api/device-test-result/', auth='public', methods=["POST"], csrf=False)
    def test(self, **kw):
        return http_log_response('devices-test-result', 'OK')

    @http.route('/api/device-record/', auth='public', methods=["POST"], csrf=False)
    def object(self, **kw):
        return http_log_response('devices-record', 'OK')
