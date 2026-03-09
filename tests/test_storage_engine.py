import unittest
import os
import shutil
from storage_engine import StorageEngine


class TestStorageEngine(unittest.TestCase):

    def setUp(self):
        # Clean environment before each test
        if os.path.exists("data"):
            shutil.rmtree("data")

        if os.path.exists("wal.log"):
            os.remove("wal.log")

        os.makedirs("data", exist_ok=True)

        self.engine = StorageEngine()

    def tearDown(self):
        if os.path.exists("data"):
            shutil.rmtree("data")

        if os.path.exists("wal.log"):
            os.remove("wal.log")

    def test_put_and_read(self):
        self.engine.put("key1", "value1")
        result = self.engine.read("key1")
        self.assertEqual(result, "value1")

    def test_delete(self):
        self.engine.put("key1", "value1")
        self.engine.delete("key1")

        result = self.engine.read("key1")
        self.assertIsNone(result)

    def test_batch_put(self):
        items = [("a", "1"), ("b", "2"), ("c", "3")]
        self.engine.batch_put(items)

        self.assertEqual(self.engine.read("a"), "1")
        self.assertEqual(self.engine.read("b"), "2")
        self.assertEqual(self.engine.read("c"), "3")

    def test_range_query(self):
        self.engine.put("a", "1")
        self.engine.put("b", "2")
        self.engine.put("c", "3")

        result = self.engine.read_range("a", "c")

        self.assertEqual(result["a"], "1")
        self.assertEqual(result["b"], "2")
        self.assertEqual(result["c"], "3")

    def test_wal_recovery(self):
        self.engine.put("recover_key", "recover_value")

        # Simulate restart
        new_engine = StorageEngine()

        result = new_engine.read("recover_key")
        self.assertEqual(result, "recover_value")


if __name__ == "__main__":
    unittest.main()