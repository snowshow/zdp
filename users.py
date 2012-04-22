
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
users.set("shykes", {"email": "solomon@dotcloud.com"})
users.set("andrea", {"email": "andrea@dotcloud.com"})
users.set("sam", {"email": "sam@dotcloud.com"})
users.set("eric", {"email": "eric@dotcloud.com"})
users.set("jr", {"email": "jr@dotcloud.com"})
users.set("joffrey", {"email": "joffrey@dotcloud.com"})
users.set("yusuf", {"email": "yusuf@dotcloud.com"})
users.set("jed", {"email": "jed@dotcloud.com"})
users.set("jerome", {"email": "jerome@dotcloud.com"})
users.set("ken", {"email": "ken@dotcloud.com"})
users.set("louis", {"email": "louis@dotcloud.com"})
users.set("chris", {"email": "chris@dotcloud.com"})
users.set("elena", {"email": "elena@dotcloud.com"})
users.set("yannis", {"email": "yannis@dotcloud.com"})
users.set("charles", {"email": "charles@dotcloud.com"})


class UserService:

    @zerorpc.stream
    def subscribe_all_users(self):
        """ Subscribe to a collection of all users, with real-time synchronization."""
        for (id, doc) in users:
            yield ["set", id, doc]
        for change in users.changes:
            yield change

    def get_all_users(self):
        """ Get a list of all users. """
        return dict((id, doc) for (id, doc) in users)

    def set_user_email(self, id, email):
        """ Change the email of a user. """
        data = users.get(id)
        data['email'] = email
        users.set(id, data)

    def set_user_pic(self, id, pic):
        """ Change the profile picture of a user. """
        data = users.get(id)
        data['pic'] = pic
        users.set(id, data)

    def add_user(self, id, email):
        """ Create a new user and set its email.  """
        users.set(id, {'email': email})

    def rename_user(self, id, first_name, last_name):
        """ Change the first and last name of a user. """
        data = users.get(id)
        data['first_name'] = first_name
        data['last_name'] = last_name
        users.set(id, data)

    def capitalize_all_names(self):
        """ Capitalize the first and last name of all users. """
        for (id, doc) in users:
            doc['first_name'] = doc.get('first_name', '').capitalize()
            doc['last_name'] = doc.get('last_name', '').capitalize()
            users.set(id, doc)

    def uppercase_all_names(self):
        """ Change to uppercase the first and last name of all users. """
        for (id, doc) in users:
            doc['first_name'] = doc.get('first_name', '').upper()
            doc['last_name'] = doc.get('last_name', '').upper()
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
