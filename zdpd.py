
import os
import sys
import json
import types
import urlparse

import zerorpc
import paste.urlparser
import gevent, gevent.pywsgi
from geventwebsocket.handler import WebSocketHandler


class WSRPC:

    def __init__(self, service):
        self._service = service

    def extract_zerorpc_info(self, environ):
        method_name = environ["PATH_INFO"][1:]
        args = urlparse.parse_qs(environ["QUERY_STRING"]).get("a", [])
        return (method_name, args)

    def wsgiapp(self, environ, start_response):
#        for k, v in environ.items():
#            print "{0} = {1}".format(k, v)
        print environ["PATH_INFO"]
        ws = environ['wsgi.websocket'] 
        method_name, args = self.extract_zerorpc_info(environ)
        print "Zerorpc call: {0} {1}".format(method_name, args)
        result = getattr(self._service, method_name)(*args)
        if isinstance(result, types.GeneratorType):
            for item in result:
                ws.send(json.dumps(item))
        else:
            ws.send(json.dumps(result))

    def run(self, host, port):
        gevent.pywsgi.WSGIServer((host, port), self.wsgiapp, handler_class=WebSocketHandler).start()


if __name__ == '__main__':
    zerorpc_connect, ws_port = sys.argv[1], sys.argv[2]
    service = zerorpc.Client()
    service.connect(zerorpc_connect)
    WSRPC(service).run('', int(ws_port))
    while True:
        gevent.sleep()
