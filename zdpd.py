
import os
import sys
import json
import uuid

import zerorpc
import paste.urlparser
import gevent, gevent.pywsgi
from geventwebsocket.handler import WebSocketHandler


class DB:
    """ A database with push capabilities. """

    def __init__(self):
        self._docs = {}
        self._feeds = {}

    @property
    def changes(self):
        feed_id = str(uuid.uuid4())
        self._feeds[feed_id] = gevent.queue.Queue()
        try:
            for change in self._feeds[feed_id]:
                yield change
        finally:
            del self._feeds[feed_id]

    def publish_change(self, change):
        for feed in self._feeds.values():
            feed.put(change)

    def set(self, id, doc):
        self._docs[id] = doc
        self.publish_change(['set', id, doc])

    def get(self, id):
        return self._docs[id]

    def __iter__(self):
        return iter(self._docs.items())

    def delete(self, id):
        self.publish_change(['delete', id])
        del self._docs[id]



users = DB()
users.set("shykes", {
        "first_name": "Solomon",
        "last_name": "Hykes",
        "email": "solomon@dotcloud.com"
})
users.set("gordon", {
        "first_name": "Gordon",
        "last_name": "the turtle",
        "email": "gordon@dotcloud.com"
})


class UserService:

    @zerorpc.stream
    def get_all_users(self):
        for (id, doc) in users:
            yield ["set", id, doc]
        for change in users.changes:
            yield change

    def set_user_email(self, id, email):
        data = users.get(id)
        data['email'] = email
        users.set(id, data)

    def set_user_pic(self, id, pic):
        data = users.get(id)
        data['pic'] = pic
        users.set(id, data)

    def add_user(self, id, email, first_name, last_name):
        users.set(id, {'email': email, 'first_name': first_name, 'last_name': last_name})

    def test(self):
        return "test!"


class WSRPC:

    def __init__(self, service):
        self._service = service

    def wsgiapp(self, environ, start_response):
        for k, v in environ.items():
            print "{0} = {1}".format(k, v)
        ws = environ['wsgi.websocket'] 
        method = getattr(self._service, environ['PATH_INFO'][1:])
        result = method()
        if isinstance(method, zerorpc.stream):
            for item in result:
                ws.send(json.dumps(item))
        else:
            ws.send(json.dumps(result))

    def run(self, host, port):
        gevent.pywsgi.WSGIServer((host, port), self.wsgiapp, handler_class=WebSocketHandler).start()


if __name__ == '__main__':
    user_service = UserService()
    ws = WSRPC(user_service)
    ws.run('', 9999)
    zeroservice = zerorpc.Server(user_service)
    zeroservice.bind("tcp://:4242")
    zeroservice.run()
    
