from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse

from storage_engine import StorageEngine

engine = StorageEngine()


class KVHandler(BaseHTTPRequestHandler):

    def _send(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):

        length = int(self.headers.get('Content-Length'))
        body = json.loads(self.rfile.read(length))

        if self.path == "/put":

            engine.put(body["key"], body["value"])
            self._send({"status": "ok"})

        elif self.path == "/batch_put":

            items = [(i["key"], i["value"]) for i in body["items"]]
            engine.batch_put(items)
            self._send({"status": "ok"})

    def do_GET(self):

        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/read":

            query = urllib.parse.parse_qs(parsed.query)
            key = query["key"][0]

            value = engine.read(key)

            self._send({"value": value})

        elif parsed.path == "/range":

            query = urllib.parse.parse_qs(parsed.query)

            start = query["start"][0]
            end = query["end"][0]

            result = engine.read_range(start, end)

            self._send(result)

    def do_DELETE(self):

        key = self.path.split("/")[-1]

        engine.delete(key)

        self._send({"status": "deleted"})


def run():
    server = HTTPServer(("0.0.0.0", 8080), KVHandler)
    print("KV Store running on port 8080")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down KV Store...")
        server.server_close()


if __name__ == "__main__":
    run()