
import uuid
import gevent
import zerorpc


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
    def subscribe_all_users(self):
        for (id, doc) in users:
            yield ["set", id, doc]
        for change in users.changes:
            yield change

    def get_all_users(self):
        return dict((id, doc) for (id, doc) in users)

    def set_user_email(self, id, email):
        data = users.get(id)
        data['email'] = email
        users.set(id, data)

    def set_user_pic(self, id, pic):
        data = users.get(id)
        data['pic'] = pic
        users.set(id, data)

    def add_user(self, id, email):
        users.set(id, {'email': email})

    def rename_user(self, id, first_name, last_name):
        data = users.get(id)
        data['first_name'] = first_name
        data['last_name'] = last_name
        users.set(id, data)

    def capitalize_all_names(self):
        for (id, doc) in users:
            doc['first_name'] = doc['first_name'].capitalize()
            doc['last_name'] = doc['last_name'].capitalize()
            users.set(id, doc)

    def uppercase_all_names(self):
        for (id, doc) in users:
            doc['first_name'] = doc['first_name'].upper()
            doc['last_name'] = doc['last_name'].upper()
            users.set(id, doc)



    def test(self):
        return "test!"


def main():
    user_service = UserService()
    zeroservice = zerorpc.Server(user_service)
    zeroservice.bind("tcp://:4242")
    zeroservice.run()

if __name__ == '__main__':
    main()
