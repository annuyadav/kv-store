from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse

from storage.engine import StorageEngine
from app.handlers import KVHandler
from app.config import PORT

engine = StorageEngine()
handler = KVHandler(engine)


class RequestHandler(BaseHTTPRequestHandler):

    def _send(self, data):

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):

        length = int(self.headers.get("Content-Length"))
        body = json.loads(self.rfile.read(length))

        if self.path == "/put":

            result = handler.handle_put(body)

        elif self.path == "/batch_put":

            result = handler.handle_batch_put(body)

        self._send(result)

    def do_GET(self):

        parsed = urllib.parse.urlparse(self.path)

        query = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/read":

            result = handler.handle_read(query)

        elif parsed.path == "/range":

            result = handler.handle_range(query)

        else:

            result = {"error": "Invalid endpoint"}

        self._send(result)

    def do_DELETE(self):

        key = self.path.split("/")[-1]

        result = handler.handle_delete(key)

        self._send(result)


def start_server():

    server = HTTPServer(("0.0.0.0", PORT), RequestHandler)

    print(f"KV Store running on port {PORT}")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("Shutting down server")
        server.server_close()