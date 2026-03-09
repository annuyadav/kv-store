import json
import urllib.parse


class KVHandler:

    def __init__(self, engine):
        self.engine = engine

    def handle_put(self, body):

        key = body["key"]
        value = body["value"]

        self.engine.put(key, value)

        return {"status": "ok"}

    def handle_batch_put(self, body):

        items = [(i["key"], i["value"]) for i in body["items"]]

        self.engine.batch_put(items)

        return {"status": "ok"}

    def handle_read(self, query):

        key = query["key"][0]

        value = self.engine.read(key)

        return {"value": value}

    def handle_range(self, query):

        start = query["start"][0]
        end = query["end"][0]

        return self.engine.read_range(start, end)

    def handle_delete(self, key):

        self.engine.delete(key)

        return {"status": "deleted"}