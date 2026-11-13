import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from serve import Handler


class ServeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=5) as response:
                return response.status, response.read().decode()
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode()

    def test_health_answers_ok(self):
        self.assertEqual(self.get("/health"), (200, "ok"))

    def test_a_quote_to_nz_answers_the_international_rate(self):
        status, body = self.get("/quote?country=NZ&weight_kg=2")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"country": "NZ", "quote": 16.5})
        self.assertIn("16.5", body)

    def test_a_failing_quote_answers_500_with_the_exception(self):
        status, body = self.get("/quote?country=NZ&weight_kg=heavy")
        self.assertEqual(status, 500)
        self.assertIn("ValueError", body)


if __name__ == "__main__":
    unittest.main()
