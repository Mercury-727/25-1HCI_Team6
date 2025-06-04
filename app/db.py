class InMemoryDB:
    def __init__(self):
        self.db = {}

    def _get_user_db(self, uuid):
        if not self._is_user_exist(uuid):
            self.db[uuid] = {}

        return self.db[uuid]

    def _is_user_exist(self, uuid):
        return uuid in self.db

    def put(self, uuid, key, value):
        user_db = self._get_user_db(uuid)
        user_db[key] = value

    def get(self, uuid, key, default=None):
        user_db = self._get_user_db(uuid)
        return user_db.get(key, default)
