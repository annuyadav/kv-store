import unittest
import threading
import time
import json
from urllib import request

from app.server import start_server


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.server_thread = threading.Thread(target=start_server, daemon=True)
        cls.server_thread.start()

        time.sleep(1)

    def test_put_api(self):

        data = json.dumps({
            "key": "api_key",
            "value": "api_value"
        }).encode()

        req = request.Request(
            "http://localhost:8080/put",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        response = request.urlopen(req)

        result = json.loads(response.read())

        self.assertEqual(result["status"], "ok")

    def test_read_api(self):

        response = request.urlopen(
            "http://localhost:8080/read?key=api_key"
        )

        result = json.loads(response.read())

        self.assertEqual(result["value"], "api_value")


if __name__ == "__main__":
    unittest.main()